from os import devnull
import subprocess

def encode(s):
    try:
        return s.encode('utf-8')
    except (AttributeError, SyntaxError):
        pass
    return s

# In Python 3, all strings are sequences of Unicode characters.
# There is a bytes type that holds raw bytes.
# In Python 2, a string may be of type str or of type unicode.
def decode(s):
    try:
        return s.decode('utf-8')
    except (AttributeError, SyntaxError, UnicodeEncodeError):
        pass
    return s

def is_command_valid(command):
    """Check if the command is recognized on the machine. It is used to determine the installation of the 'less' pager. If the command is empty or if calling the command silently throws an OSError, the function returns False. Otherwise, it returns True.
    Input-Output Arguments
    :param command: String. The command to be checked.
    :return: Bool. True if the command is recognized, False otherwise.
    """