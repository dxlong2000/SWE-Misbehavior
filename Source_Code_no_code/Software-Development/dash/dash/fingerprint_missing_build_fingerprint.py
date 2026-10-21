import re

cache_regex = re.compile(r"^v[\w-]+m[0-9a-fA-F]+$")
version_clean = re.compile(r"[^\w-]")


def build_fingerprint(path, version, hash_value):
    """This function builds a fingerprint for a file based on the given path, version, and hash value. It extracts the filename and extension from the path, constructs a file path without the filename, replaces the version with underscores, and concatenates all the parts to form the fingerprint. The format of a fingerprint is "{file_path}.v{v_str}m{hash_value}.{extension}".
    Input-Output Arguments
    :param path: String. The path of the file.
    :param version: Any data type. The version of the file.
    :param hash_value: Any data type. The hash value of the file.
    :return: String. The fingerprint of the file.
    """


def check_fingerprint(path):
    path_parts = path.split("/")
    name_parts = path_parts[-1].split(".")

    # Check if the resource has a fingerprint
    if len(name_parts) > 2 and cache_regex.match(name_parts[1]):
        original_name = ".".join([name_parts[0]] + name_parts[2:])
        return "/".join(path_parts[:-1] + [original_name]), True

    return path, False