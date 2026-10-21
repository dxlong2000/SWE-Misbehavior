# pylint: disable=C0103, C0111, W0703, R0903
import os


class MacVendorDB:
    """Maps from MACs to Manufacturers via the IEEE Organizationally Unique Identifier (oui) list."""
    def __init__(self, oui_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'oui.txt')):
        self.db = {}
        with open(oui_file, 'r') as f:
            for line in f.readlines():
                mac, vendor = line.split('=', maxsplit=1)
                self.db[mac] = vendor.strip()

    def lookup(self, mac):
        """This function looks up the manufacturer name based on the MAC address provided. It takes a MAC address as input, converts it to uppercase and removes the colons. It then checks if the first 6 characters (':' removed) of the MAC address match any prefix in the database. If there is a match, it returns the corresponding manufacturer name.
        Input-Output Arguments
        :param self: MacVendorDB. An instance of the MacVendorDB class.
        :param mac: String. The MAC address to lookup the manufacturer for.
        :return: String. The manufacturer name corresponding to the MAC address. If no match is found, an empty string is returned.
        """