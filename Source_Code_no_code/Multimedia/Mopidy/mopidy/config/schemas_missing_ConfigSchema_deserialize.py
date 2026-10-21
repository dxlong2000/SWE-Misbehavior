import collections




def _did_you_mean(name, choices):
    """Suggest most likely setting based on levenshtein."""
    if not choices:
        return None

    name = name.lower()
    candidates = [(_levenshtein(name, c), c) for c in choices]
    candidates.sort()

    if candidates[0][0] <= 3:
        return candidates[0][1]
    return None


def _levenshtein(a, b):
    """Calculates the Levenshtein distance between a and b."""
    n, m = len(a), len(b)
    if n > m:
        return _levenshtein(b, a)

    current = range(n + 1)
    for i in range(1, m + 1):
        previous, current = current, [i] + [0] * n
        for j in range(1, n + 1):
            add, delete = previous[j] + 1, current[j - 1] + 1
            change = previous[j - 1]
            if a[j - 1] != b[i - 1]:
                change += 1
            current[j] = min(add, delete, change)
    return current[n]


class ConfigSchema(collections.OrderedDict):

    """Logical group of config values that correspond to a config section.

    Schemas are set up by assigning config keys with config values to
    instances. Once setup :meth:`deserialize` can be called with a dict of
    values to process. For convienience we also support :meth:`format` method
    that can used for converting the values to a dict that can be printed and
    :meth:`serialize` for converting the values to a form suitable for
    persistence.
    """

    def __init__(self, name):
        super().__init__()
        self.name = name

    def deserialize(self, values):
        """This function validates the given `values` using the config schema. It iterates through each key-value pair in the `values` dictionary and tries to deserialize the value using the corresponding schema in the config. If the key is not found in the schema, it adds an error message to the `errors` dictionary. If the deserialization fails, it adds the error message to the `errors` dictionary and sets the value to None in the `result` dictionary. After iterating through all the keys in the schema, it checks for any deprecated keys and removes them from the `result` dictionary. Finally, it returns a tuple containing the cleaned values in the `result` dictionary and the errors in the `errors` dictionary.
        Input-Output Arguments
        :param self: ConfigSchema. An instance of the ConfigSchema class.
        :param values: dict. A dictionary containing the values to be validated against the config schema.
        :return: tuple. A tuple containing the cleaned values in the `result` dictionary and the errors in the `errors` dictionary.
        """

    def serialize(self, values, display=False):
        """Converts the given ``values`` to a format suitable for persistence.

        If ``display`` is :class:`True` secret config values, like passwords,
        will be masked out.

        Returns a dict of config keys and values."""
        result = collections.OrderedDict()
        for key in self.keys():
            if key in values:
                result[key] = self[key].serialize(values[key], display)
        return result


class MapConfigSchema:

    """Schema for handling multiple unknown keys with the same type.

    Does not sub-class :class:`ConfigSchema`, but implements the same
    serialize/deserialize interface.
    """

    def __init__(self, name, value_type):
        self.name = name
        self._value_type = value_type

    def deserialize(self, values):
        errors = {}
        result = {}

        for key, value in values.items():
            try:
                result[key] = self._value_type.deserialize(value)
            except ValueError as e:  # deserialization failed
                result[key] = None
                errors[key] = str(e)
        return result, errors

    def serialize(self, values, display=False):
        result = collections.OrderedDict()
        for key in sorted(values.keys()):
            result[key] = self._value_type.serialize(values[key], display)
        return result