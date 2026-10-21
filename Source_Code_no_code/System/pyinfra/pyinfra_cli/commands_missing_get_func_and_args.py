from __future__ import annotations

import json

from pyinfra.api.facts import FactBase

from .exceptions import CliError
from .util import try_import_module_attribute


def get_func_and_args(commands):
    """This function takes a list of commands as input and returns the corresponding operation function and its arguments. It first extracts the operation name from the commands list and imports the corresponding module attribute. Then, it parses the arguments and returns them along with the operation function.
    Input-Output Arguments
    :param commands: List of strings. The list of commands to be processed.
    :return: Tuple. The operation function and its arguments.
    """


def get_facts_and_args(commands):
    facts: list[FactBase] = []

    current_fact = None

    for command in commands:
        if "=" in command:
            if not current_fact:
                raise CliError("Invalid fact commands: `{0}`".format(commands))

            key, value = command.split("=", 1)
            current_fact[2][key] = value
            continue

        if current_fact:
            facts.append(current_fact)
            current_fact = None

        if "." not in command:
            raise CliError(f"Invalid fact: `{command}`, should be in the format `module.cls`")

        fact_cls = try_import_module_attribute(command, prefix="pyinfra.facts")
        current_fact = (fact_cls, (), {})

    if current_fact:
        facts.append(current_fact)

    return facts