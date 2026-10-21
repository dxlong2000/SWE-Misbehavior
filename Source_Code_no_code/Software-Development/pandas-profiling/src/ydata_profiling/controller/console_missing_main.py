"""This file add the console interface to the package."""
import argparse
from pathlib import Path
from typing import Any, List, Optional

from ydata_profiling.__init__ import ProfileReport, __version__



def parse_args(args: Optional[List[Any]] = None) -> argparse.Namespace:
    """Parse the command line arguments for the `ydata_profiling` binary.

    Args:
      args: List of input arguments. (Default value=None).

    Returns:
      Namespace with parsed arguments.

    """
    parser = argparse.ArgumentParser(
        description="Profile the variables in a CSV file and generate a HTML report."
    )

    # Version
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    # Console specific
    parser.add_argument(
        "-s",
        "--silent",
        help="Only generate but do not open report",
        action="store_true",
    )

    parser.add_argument(
        "-m",
        "--minimal",
        help="Minimal configuration for big data sets",
        action="store_true",
    )

    parser.add_argument(
        "-e",
        "--explorative",
        help="Explorative configuration featuring unicode, file and image analysis",
        action="store_true",
    )

    # Config
    parser.add_argument(
        "--pool_size", type=int, default=0, help="Number of CPU cores to use"
    )
    parser.add_argument(
        "--title",
        type=str,
        default="Pandas Profiling Report",
        help="Title for the report",
    )

    parser.add_argument(
        "--infer_dtypes",
        default=False,
        action="store_true",
        help="To infer dtypes of the dataframe",
    )

    parser.add_argument(
        "--no-infer_dtypes",
        dest="infer_dtypes",
        action="store_false",
        help="To read dtypes as read by pandas",
    )

    parser.add_argument(
        "--config_file",
        type=str,
        default=None,
        help="Specify a yaml config file. Have a look at the 'config_default.yaml' as a starting point.",
    )

    parser.add_argument(
        "input_file",
        type=str,
        help="CSV file (or other file type supported by pandas) to profile",
    )
    parser.add_argument(
        "output_file",
        type=str,
        nargs="?",
        help="Output report file. If empty, replaces the input_file's extension with .html and uses that.",
        default=None,
    )

    return parser.parse_args(args)


def main(args: Optional[List[Any]] = None) -> None:
    """This function is the main entry point for running another corresponding package. It takes in arguments, parses them, and generates a profiling report based on the input data.
    Input-Output Arguments
    :param args: Optional list of any type. Arguments for the program. Defaults to None.
    :return: None.
    """