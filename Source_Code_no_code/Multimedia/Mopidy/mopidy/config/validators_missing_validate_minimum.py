# TODO: add validate regexp?


def validate_required(value, required):
    """Validate that ``value`` is set if ``required``

    Normally called in :meth:`~mopidy.config.types.ConfigValue.deserialize` on
    the raw string, _not_ the converted value.
    """
    if required and not value:
        raise ValueError("must be set.")


def validate_choice(value, choices):
    """Validate that ``value`` is one of the ``choices``

    Normally called in :meth:`~mopidy.config.types.ConfigValue.deserialize`.
    """
    if choices is not None and value not in choices:
        names = ", ".join(repr(c) for c in choices)
        raise ValueError(f"must be one of {names}, not {value}.")


def validate_minimum(value, minimum):
    """This function validates that the input value is at least the minimum value. If the input value is less than the minimum value, it raises a ValueError in the format "{value!r} must be larger than {minimum!r}.".
    Input-Output Arguments
    :param value: The input value to be validated.
    :param minimum: The minimum value that the input value should be compared against.
    :return: No return values.
    """


def validate_maximum(value, maximum):
    """Validate that ``value`` is at most ``maximum``

    Normally called in :meth:`~mopidy.config.types.ConfigValue.deserialize`.
    """
    if maximum is not None and value > maximum:
        raise ValueError(f"{value!r} must be smaller than {maximum!r}.")