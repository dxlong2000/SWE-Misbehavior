import logging
import sys
from functools import wraps
from time import sleep

from pymongo.errors import (AutoReconnect, OperationFailure, DuplicateKeyError, ServerSelectionTimeoutError,
                            BulkWriteError)

from .hooks import log_exception as _log_exception

logger = logging.getLogger(__name__)

_MAX_RETRIES = 15


def _get_host(store):
    ret = {}
    if store:
        try:
            if isinstance(store, (list, tuple)):
                store = store[0]
            ret['l'] = store._arctic_lib.get_name()
            ret['mnodes'] = ["{}:{}".format(h, p) for h, p in store._collection.database.client.nodes]
            ret['mhost'] = "{}".format(store._arctic_lib.arctic.mongo_host)
        except Exception:
            # Sometimes get_name(), for example, fails if we're not connected to MongoDB.
            pass
    return ret


_in_retry = False
_retry_count = 0


def mongo_retry(f):
    """This function is a decorator that handles AutoReconnect and OperationFailure errors from PyMongo. It catches all exceptions and logs them if the module name contains 'arctic' and finally set the global attribute _retry_count and _in_retry.
    Input-Output Arguments
    :param f: The function to be decorated.
    :return: The decorated function.
    """


def _handle_error(f, e, retry_count, **kwargs):
    if retry_count > _MAX_RETRIES:
        logger.error('Too many retries %s [%s], raising' % (f.__name__, e))
        e.traceback = sys.exc_info()[2]
        raise
    log_fn = logger.warning if retry_count > 2 else logger.debug
    log_fn('%s %s [%s], retrying %i' % (type(e), f.__name__, e, retry_count))
    # Log operation failure errors
    _log_exception(f.__name__, e, retry_count, **kwargs)
#    if 'unauthorized' in str(e):
#        raise
    sleep(0.01 * min((3 ** retry_count), 50))  # backoff...