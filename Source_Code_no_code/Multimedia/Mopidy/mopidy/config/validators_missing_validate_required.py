# TODO: add validate regexp?


def validate_required(value, required):
    """This function validates that the value is set if it is required. It is normally called in the mopidy.config.types.ConfigValue.deserialize method on the raw string, not the converted value.
    Input-Output Arguments
    :param value: The value to be validated.
    :param required: Boolean. Whether the value is required or not.
    :return: No return values.
    """


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
    """Validate that ``value`` is at most ``maximum``

    Normally called in :meth:`~mopidy.config.types.ConfigValue.deserialize`.
    """
    if maximum is not None and value > maximum:
        raise ValueError(f"{value!r} must be smaller than {maximum!r}.")