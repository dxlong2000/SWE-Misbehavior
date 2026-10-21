from pandas import DataFrame, Series

from ._chunker import Chunker


class PassthroughChunker(Chunker):
    TYPE = 'passthru'

    def to_chunks(self, df, **kwargs):
        """
        pass thru chunker of the dataframe/series

        returns
        -------
        ('NA', 'NA', 'NA', dataframe/series)
        """
        if len(df) > 0:
            yield b'NA', b'NA', b'NA', df

    def to_range(self, start, end):
        """
        returns a RangeObject from start/end sentinels.

        returns
        -------
        string
        """
        return b'NA'

    def chunk_to_str(self, chunk_id):
        """
        Converts parts of a chunk range (start or end) to a string

        returns
        -------
        string
        """
        return b'NA'

    def to_mongo(self, range_obj):
        """
        returns mongo query against range object.
        since range object is not valid, returns empty dict

        returns
        -------
        string
        """
        return {}

    def filter(self, data, range_obj):
        """
        ensures data is properly subset to the range in range_obj.
        since range object is not valid, returns data

        returns
        -------
        data
        """
        return data

    def exclude(self, data, range_obj):
        """This function removes data within the bounds of the range object. Since the range object is not valid for this chunk type, it returns an empty dataframe or series.
        Input-Output Arguments
        :param self: PassthroughChunker. An instance of the PassthroughChunker class.
        :param data: DataFrame or Series. The data to be processed.
        :param range_obj: Range object. The range object to be used for exclusion.
        :return: Empty DataFrame or Series. The result of the exclusion process.
        """