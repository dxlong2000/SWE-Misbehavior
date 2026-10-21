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
    """Validate that ``value`` is at least ``minimum``

    Normally called in :meth:`~mopidy.config.types.ConfigValue.deserialize`.
    """
    if minimum is not None and value < minimum:
        raise ValueError(f"{value!r} must be larger than {minimum!r}.")


def validate_maximum(value, maximum):
    """This function validates that the given value is at most the given maximum value. If the maximum is not None or value is bigger than maximum, it raises a ValueError in the format ""{value!r} must be smaller than {maximum!r}.".
    Input-Output Arguments
    :param value: The value to be validated.
    :param maximum: The maximum value that the given value should not exceed.
    :return: No return values.
    """