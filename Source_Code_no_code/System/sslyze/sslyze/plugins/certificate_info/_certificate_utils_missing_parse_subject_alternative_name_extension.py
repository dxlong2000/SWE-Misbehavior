from dataclasses import dataclass
from hashlib import sha256
from typing import List, cast

from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from cryptography.x509 import (
    ExtensionOID,
    DNSName,
    ExtensionNotFound,
    NameOID,
    DuplicateExtension,
    IPAddress,
    Certificate,
    SubjectAlternativeName,
    Name,
)


@dataclass(frozen=True)
class SubjectAlternativeNameExtension:
    dns_names: List[str]
    ip_addresses: List[str]


def parse_subject_alternative_name_extension(certificate: Certificate) -> SubjectAlternativeNameExtension:
    """This function parses the Subject Alternative Name (SAN) extension of a certificate. It retrieves the SAN extension from the certificate and extracts the DNS names and IP addresses from it. It then returns a SubjectAlternativeNameExtension object containing the extracted DNS names and IP addresses.
    Input-Output Arguments
    :param certificate: Certificate. The certificate from which to parse the SAN extension.
    :return: SubjectAlternativeNameExtension. An object containing the extracted DNS names and IP addresses from the SAN extension.
    """


def get_common_names(name_field: Name) -> List[str]:
    return [cn.value for cn in name_field.get_attributes_for_oid(NameOID.COMMON_NAME)]  # type: ignore


def get_public_key_sha256(certificate: Certificate) -> bytes:
    pub_bytes = certificate.public_key().public_bytes(encoding=Encoding.DER, format=PublicFormat.SubjectPublicKeyInfo)
    digest = sha256(pub_bytes).digest()
    return digest