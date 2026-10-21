"""Module for LocalDirectoryRecordSource"""
import logging
import os

from toolz import pipe
from toolz.curried import filter as filterz
from toolz.curried import last as lastz
from toolz.curried import map as mapz
from toolz.curried import mapcat as mapcatz
from toolz.curried import sorted as sortedz

from trailscraper.cloudtrail import LogFile


class LocalDirectoryRecordSource():
    """Class to represent cloudtrail records stored on disk"""
    def __init__(self, log_dir):
        self._log_dir = log_dir

    def _valid_log_files(self):
        def _valid_or_warn(log_file):
            if log_file.has_valid_filename():
                return True

            logging.warning("Invalid filename: %s", log_file.filename())
            return False

        def _to_paths(triple):
            root, _, files_in_dir = triple
            return [os.path.join(root, file_in_dir) for file_in_dir in files_in_dir]

        return pipe(os.walk(self._log_dir),
                    mapcatz(_to_paths),
                    mapz(LogFile),
                    filterz(_valid_or_warn))

    def load_from_dir(self, from_date, to_date):
        """Load all CloudTrail records from a directory within a specified date range. It iterates through all valid log files in the directory and checks if each file contains events within the specified date range. If a file meets the criteria, it retrieves the records from that file and adds them to the list of records.
        Input-Output Arguments
        :param self: LocalDirectoryRecordSource. An instance of the LocalDirectoryRecordSource class.
        :param from_date: The starting date of the desired records.
        :param to_date: The ending date of the desired records.
        :return: List of CloudTrail records. The records that fall within the specified date range.
        """

    def last_event_timestamp_in_dir(self):
        """Return the timestamp of the most recent event in the given directory"""
        most_recent_file = pipe(self._valid_log_files(),
                                sortedz(key=LogFile.timestamp),
                                lastz,
                                LogFile.records,
                                sortedz(key=lambda record: record.event_time),
                                lastz)

        return most_recent_file.event_time