import gc
import gevent

from wal_e import channel
from wal_e import tar_partition



class TarUploadPool(object):
    def __init__(self, uploader, max_concurrency,
                 max_members=tar_partition.PARTITION_MAX_MEMBERS):
        # Injected upload mechanism
        self.uploader = uploader

        # Concurrency maximums
        self.max_members = max_members
        self.max_concurrency = max_concurrency

        # Current concurrency burden
        self.member_burden = 0

        # Synchronization and tasks
        self.wait_change = channel.Channel()
        self.closed = False

        # Used for both synchronization and measurement.
        self.concurrency_burden = 0

    def _start(self, tpart):
        """Start upload and accout for resource consumption."""
        g = gevent.Greenlet(self.uploader, tpart)
        g.link(self._finish)

        # Account for concurrency_burden before starting the greenlet
        # to avoid racing against .join.
        self.concurrency_burden += 1

        self.member_burden += len(tpart)

        g.start()

    def _finish(self, g):
        """Called on completion of an upload greenlet.

        Takes care to forward Exceptions or, if there is no error, the
        finished TarPartition value across a channel.
        """
        assert g.ready()

        if g.successful():
            finished_tpart = g.get()
            self.wait_change.put(finished_tpart)
        else:
            self.wait_change.put(g.exception)

    def _wait(self):
        """Block until an upload finishes

        Raise an exception if that tar volume failed with an error.
        """
        val = self.wait_change.get()

        if isinstance(val, Exception):
            # Don't other uncharging, because execution is going to stop
            raise val
        else:
            # Uncharge for resources.
            self.member_burden -= len(val)
            self.concurrency_burden -= 1

    def put(self, tpart):
        """This function is used to upload a tar volume. It checks if there is too much work outstanding already and raises errors of previously submitted greenlets that die unexpectedly. If there are not enough resources to start an upload, it raises an exception. Otherwise, it starts the upload.
        Input-Output Arguments
        :param self: TarUploadPool. An instance of the TarUploadPool class.
        :param tpart: The tar volume to be uploaded.
        :return: No return values.
        """

    def join(self):
        """Wait for uploads to exit, raising errors as necessary."""
        self.closed = True

        while self.concurrency_burden > 0:
            self._wait()