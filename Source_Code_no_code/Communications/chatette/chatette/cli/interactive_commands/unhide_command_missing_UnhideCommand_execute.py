"""
Module `chatette.cli.interactive_commands.unhide_command`.
Contains the strategy class that represents the interacive mode command
`unhide` which restores a unit definition that has been hidden.
"""

from chatette.cli.interactive_commands.command_strategy import CommandStrategy
from chatette.cli.interactive_commands.hide_command import HideCommand

from chatette.units.ast import AST


class UnhideCommand(CommandStrategy):
    def execute(self):
        """This function implements the command `unhide` which restores a unit definition that was hidden from the AST. It takes input arguments and performs certain actions based on the input. Initially, the function checks if the number of command tokens is less than three. It determines the unit type from the second command token and validate the type of unit. It tries to interpret the third command token as a regular expression and execute the restoration process on the unit with different regular expression conditions.
        Input-Output Arguments
        :param self: UnhideCommand. An instance of the UnhideCommand class.
        :return: No return values.
        """

    def execute_on_unit(self, unit_type, unit_name, variation_name=None):
        if variation_name is None:
            try:
                unit = HideCommand.stored_units[unit_type.name][unit_name]
                AST.get_or_create().add_unit(unit, unit_type)
                del HideCommand.stored_units[unit_type.name][unit_name]
                self.print_wrapper.write(
                    unit_type.name.capitalize() + " '" + unit_name + \
                    "' was successfully restored."
                )
            except KeyError:
                self.print_wrapper.error_log(
                    unit_type.name.capitalize() + " '" + unit_name + \
                    "' was not previously hidden."
                )
            except ValueError:
                self.print_wrapper.error_log(
                    unit_type.name.capitalize() + " '" + unit_name + \
                    "' is already defined in the parser."
                )
        else:
            try:
                unit = AST.get_or_create()[unit_type][unit_name]
            except KeyError:
                self.print_wrapper.error_log(
                    unit_type.name.capitalize() + " '" + unit_name + \
                    "' is not defined."
                )
                return
            try:
                rules = \
                    HideCommand.stored_variations[unit_type.name][unit_name][variation_name]
                if variation_name in unit._variation_rules:
                    self.print_wrapper.error_log(
                        "Variation '" + variation_name + \
                        "' is already defined for " + unit_type.name + \
                        " '" + unit_name + "'."
                    )
                    return
                unit.add_all_rules(rules, variation_name)
                self.print_wrapper.write(
                    "Variation '" + variation_name + "' of " + \
                    unit_type.name + " '" + unit_name + \
                    "' was successfully restored."
                )
            except KeyError:
                self.print_wrapper.error_log(
                    "Variation '" + variation_name + \
                    "' of " + unit_type.name + " '" + unit_name + \
                    "' was not previously hidden."
                )


    # Override abstract methods
    def finish_execution(self):
        raise NotImplementedError()