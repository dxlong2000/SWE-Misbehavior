from collections import namedtuple


class VersionedItem(namedtuple('VersionedItem', ['symbol', 'library', 'data', 'version', 'metadata', 'host'])):
    """
    Class representing a Versioned object in VersionStore.
    """

    def __new__(cls, symbol, library, data, version, metadata, host=None):
        return super(VersionedItem, cls).__new__(cls, symbol, library, data, version, metadata, host)

    def metadata_dict(self):
        return {'symbol': self.symbol, 'library': self.library, 'version': self.version}

    def __repr__(self):
        return str(self)

    def __str__(self):
        """Return a string representation of the VersionedItem instance in the format "VersionedItem(symbol={symbol},library={library},data={data},version={version},metadata={metadata},host={host})".
        Input-Output Arguments
        :param self: VersionedItem. An instance of the VersionedItem class.
        :return: String. The string representation of the VersionedItem instance.
        """


ChangedItem = namedtuple('ChangedItem', ['symbol', 'orig_version', 'new_version', 'changes'])