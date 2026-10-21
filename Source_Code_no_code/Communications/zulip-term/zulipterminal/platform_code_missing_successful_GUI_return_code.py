import platform
import subprocess

from typing_extensions import Literal


# PLATFORM DETECTION
SupportedPlatforms = Literal["Linux", "MacOS", "WSL"]
AllPlatforms = Literal[SupportedPlatforms, "unsupported"]

raw_platform = platform.system()

PLATFORM: AllPlatforms

if raw_platform == "Linux":
    PLATFORM = "WSL" if "microsoft" in platform.release().lower() else "Linux"
elif raw_platform == "Darwin":
    PLATFORM = "MacOS"
else:
    PLATFORM = "unsupported"


# PLATFORM DEPENDENT HELPERS
MOUSE_SELECTION_KEY = "Fn + Alt" if PLATFORM == "MacOS" else "Shift"


def notify(title: str, text: str) -> str:
    command_list = None
    if PLATFORM == "MacOS":
        command_list = [
            "osascript",
            "-e",
            "on run(argv)",
            "-e",
            "return display notification item 1 of argv with title "
            'item 2 of argv sound name "ZT_NOTIFICATION_SOUND"',
            "-e",
            "end",
            "--",
            text,
            title,
        ]
    elif PLATFORM == "Linux":
        command_list = ["notify-send", "--", title, text]

    if command_list is not None:
        try:
            subprocess.run(
                command_list, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        except FileNotFoundError:
            # This likely means the notification command could not be found
            return command_list[0]
    return ""


def successful_GUI_return_code() -> int:
    """This function returns the success return code for GUI commands, which can be OS specific. If the platform is Windows Subsystem for Linux (WSL), it returns 1. Otherwise, it returns 0.
    Input-Output Arguments
    :param: No input parameters.
    :return: int. The success return code for GUI commands.
    """


def normalized_file_path(path: str) -> str:
    """
    Returns file paths which are normalized as per platform.
    """
    # Convert Unix path to Windows path for WSL
    if PLATFORM == "WSL":
        return path.replace("/", "\\")

    return path