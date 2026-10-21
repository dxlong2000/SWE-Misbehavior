# TODO: add validate regexp?


def validate_required(value, required):
    """Validate that ``value`` is set if ``required``

    Normally called in :meth:`~mopidy.config.types.ConfigValue.deserialize` on
    the raw string, _not_ the converted value.
    """
    if required and not value:
        raise ValueError("must be set.")


def validate_choice(value, choices):
    """This function validates whether the given value is one of the choices provided. If the value is not in the choices, it raises a ValueError in the format "must be one of {names}, not {value}.".
    Input-Output Arguments
    :param value: The value to be validated.
    :param choices: List. The list of choices to validate the value against.
    :return: No return values.
    """


def validate_minimum(value, minimum):
    """Validate that ``value`` is at least ``minimum``

    Normally called in :meth:`~mopidy.config.types.ConfigValue.deserialize`.
    """
    if minimum is not None and value < minimum:
        raise ValueError(f"{value!r} must be larger than {minimum!r}.")


def validate_maximum(value, maximum):
    """Validate that ``value`` is at most ``maximum``

    Normally called in :meth:`~mopidy.config.types.ConfigValue.deserialize`.
    """
    if maximum is not None and value > maximum:
        raise ValueError(f"{value!r} must be smaller than {maximum!r}.")