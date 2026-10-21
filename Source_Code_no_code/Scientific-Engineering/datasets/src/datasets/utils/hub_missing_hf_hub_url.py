from typing import Optional
from urllib.parse import quote

import huggingface_hub as hfh
from packaging import version


def hf_hub_url(repo_id: str, path: str, revision: Optional[str] = None) -> str:
    """This function returns the URL of a file in the Hugging Face Hub based on the given repository ID, file path, and revision. It first checks the version of the Hugging Face Hub and encodes the file path if the version is older than 0.11.0.
    Input-Output Arguments
    :param repo_id: String. The ID of the repository in the Hugging Face Hub.
    :param path: String. The file path in the repository.
    :param revision: String. The revision of the file. Defaults to None.
    :return: String. The URL of the file in the Hugging Face Hub.
    """