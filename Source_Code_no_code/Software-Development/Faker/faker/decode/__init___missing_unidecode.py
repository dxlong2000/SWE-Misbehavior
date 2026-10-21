from .codes import codes


def unidecode(txt: str) -> str:
    """This function takes a string as input and returns a new string with all non-ASCII characters replaced by their closest ASCII equivalents. It iterates over each character in the input string, checks its codepoint, and replaces it with the corresponding ASCII character if available.
    Input-Output Arguments
    :param txt: String. The input text to be processed.
    :return: String. The processed text with non-ASCII characters replaced by their closest ASCII equivalents.
    """