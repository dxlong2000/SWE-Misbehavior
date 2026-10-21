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
    """This function returns a dictionary containing the host information of the given store. It first checks if the store is not empty. If the store is not empty, it checks whether it's a list or tuple and takes the first element if so. The function then gathers the store's library name, the MongoDB nodes (formatted as "host:port"), and the MongoDB host associated with the Arctic library.
    Input-Output Arguments
    :param store: Object. The store object from which the host information is to be retrieved.
    :return: Dictionary. A dictionary containing the host information of the given store.
    """


_in_retry = False
_retry_count = 0


def mongo_retry(f):
    """
    Catch-all decorator that handles AutoReconnect and OperationFailure
    errors from PyMongo
    """
    log_all_exceptions = 'arctic' in f.__module__ if f.__module__ else False

    @wraps(f)
    def f_retry(*args, **kwargs):
        global _retry_count, _in_retry
        top_level = not _in_retry
        _in_retry = True
        try:
            while True:
                try:
                    return f(*args, **kwargs)
                except (DuplicateKeyError, ServerSelectionTimeoutError, BulkWriteError) as e:
                    # Re-raise errors that won't go away.
                    _handle_error(f, e, _retry_count, **_get_host(args))
                    raise
                except (OperationFailure, AutoReconnect) as e:
                    _retry_count += 1
                    _handle_error(f, e, _retry_count, **_get_host(args))
                except Exception as e:
                    if log_all_exceptions:
                        _log_exception(f.__name__, e, _retry_count, **_get_host(args))
                    raise
        finally:
            if top_level:
                _in_retry = False
                _retry_count = 0
    return f_retry


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