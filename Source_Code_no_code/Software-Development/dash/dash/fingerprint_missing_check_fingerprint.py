import re

cache_regex = re.compile(r"^v[\w-]+m[0-9a-fA-F]+$")
version_clean = re.compile(r"[^\w-]")


def build_fingerprint(path, version, hash_value):
    path_parts = path.split("/")
    filename, extension = path_parts[-1].split(".", 1)
    file_path = "/".join(path_parts[:-1] + [filename])
    v_str = re.sub(version_clean, "_", str(version))

    return f"{file_path}.v{v_str}m{hash_value}.{extension}"


def check_fingerprint(path):
    """This function checks if a resource file has a fingerprint in its name. If it does, it removes the fingerprint and returns the original file path along with a boolean value indicating that a fingerprint was found. If the file does not have a fingerprint, it returns the original file path along with a boolean value indicating that no fingerprint was found.
    Input-Output Arguments
    :param path: String. The file path to check for a fingerprint.
    :return: Tuple. The modified file path and a boolean value indicating if a fingerprint was found.
    """