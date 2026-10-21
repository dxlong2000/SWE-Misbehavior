import math
import struct

from pycoin.encoding.b58 import a2b_hashed_base58


LOG_2 = math.log(2)


def filter_size_required(element_count, false_positive_probability):
    # The size S of the filter in bytes is given by
    # (-1 / pow(log(2), 2) * N * log(P)) / 8
    # Of course you must ensure it does not go over the maximum size
    # (36,000: selected as it represents a filter of 20,000 items with false
    # positive rate of < 0.1% or 10,000 items and a false positive rate of < 0.0001%).
    lfpp = math.log(false_positive_probability)
    return min(36000, int(((-1 / pow(LOG_2, 2) * element_count * lfpp)+7) // 8))


def hash_function_count_required(filter_size, element_count):
    # The number of hash functions required is given by S * 8 / N * log(2).
    return int(filter_size * 8.0 / element_count * LOG_2 + 0.5)


class BloomFilter(object):
    MASK_ARRAY = [1 << _ for _ in range(8)]

    def __init__(self, size_in_bytes, hash_function_count, tweak):
        if size_in_bytes > 36000:
            raise ValueError("too large")
        self.filter_bytes = bytearray(size_in_bytes)
        self.bit_count = 8 * size_in_bytes
        self.hash_function_count = hash_function_count
        self.tweak = tweak

    def add_item(self, item_bytes):
        for hash_index in range(self.hash_function_count):
            seed = hash_index * 0xFBA4C795 + self.tweak
            self.set_bit(murmur3(item_bytes, seed=seed) % self.bit_count)

    def add_address(self, address):
        the_hash160 = a2b_hashed_base58(address)[1:]
        self.add_item(the_hash160)

    def add_hash160(self, the_hash160):
        self.add_item(the_hash160)

    def add_spendable(self, spendable):
        item_bytes = spendable.tx_hash + struct.pack("<L", spendable.tx_out_index)
        self.add_item(item_bytes)

    def _index_for_bit(self, v):
        v %= self.bit_count
        byte_index, mask_index = divmod(v, 8)
        mask = self.MASK_ARRAY[mask_index]
        return byte_index, mask

    def set_bit(self, v):
        byte_index, mask = self._index_for_bit(v)
        self.filter_bytes[byte_index] |= mask

    def check_bit(self, v):
        byte_index, mask = self._index_for_bit(v)
        return (self.filter_bytes[byte_index] & mask) == mask

    def filter_load_params(self):
        return self.filter_bytes, self.hash_function_count, self.tweak


# http://stackoverflow.com/questions/13305290/is-there-a-pure-python-implementation-of-murmurhash

def murmur3(data, seed=0):
    """Calculate the 32-bit MurmurHash3 hash value for the given data using the specified seed.
    
    Input-Output Arguments
    :param data: Bytes or bytearray, the data to be hashed.
    :param seed: Int, the seed value to initialize the hash algorithm. It defaults to 0 if not specified.
    :return: Int, the 32-bit hash value.
    
    """