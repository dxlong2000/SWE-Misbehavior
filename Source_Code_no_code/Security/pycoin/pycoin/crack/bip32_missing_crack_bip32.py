import hmac
import hashlib
import struct

from pycoin.encoding.bytes32 import from_bytes_32
from pycoin.encoding.sec import public_pair_to_sec


def ascend_bip32(bip32_pub_node, secret_exponent, child):
    """
    Given a BIP32Node with public derivation child "child" with a known private key,
    return the secret exponent for the bip32_pub_node.
    """
    i_as_bytes = struct.pack(">l", child)
    sec = public_pair_to_sec(bip32_pub_node.public_pair(), compressed=True)
    data = sec + i_as_bytes
    I64 = hmac.HMAC(key=bip32_pub_node._chain_code, msg=data, digestmod=hashlib.sha512).digest()
    I_left_as_exponent = from_bytes_32(I64[:32])
    return (secret_exponent - I_left_as_exponent) % bip32_pub_node._generator.order()


def crack_bip32(bip32_pub_node, secret_exponent, path):
    """This function cracks a BIP32 public node by iterating through a given path and updating the secret exponent. It returns a new BIP32 public node with the updated secret exponent.
    Input-Output Arguments
    :param bip32_pub_node: BIP32PublicNode. The BIP32 public node to crack.
    :param secret_exponent: int. The secret exponent to update.
    :param path: str. The path to iterate through.
    :return: BIP32PublicNode. The new BIP32 public node with the updated secret exponent.
    """