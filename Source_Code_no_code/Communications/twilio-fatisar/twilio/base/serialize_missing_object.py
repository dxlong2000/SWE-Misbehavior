import datetime
import json

from twilio.base import values


def iso8601_date(d):
    """
    Return a string representation of a date that the Twilio API understands
    Format is YYYY-MM-DD. Returns None if d is not a string, datetime, or date
    """
    if d == values.unset:
        return d
    elif isinstance(d, datetime.datetime):
        return str(d.date())
    elif isinstance(d, datetime.date):
        return str(d)
    elif isinstance(d, str):
        return d


def iso8601_datetime(d):
    """
    Return a string representation of a date that the Twilio API understands
    Format is YYYY-MM-DD. Returns None if d is not a string, datetime, or date
    """
    if d == values.unset:
        return d
    elif isinstance(d, datetime.datetime) or isinstance(d, datetime.date):
        return d.strftime("%Y-%m-%dT%H:%M:%SZ")
    elif isinstance(d, str):
        return d


def prefixed_collapsible_map(m, prefix):
    """
    Return a dict of params corresponding to those in m with the added prefix
    """
    if m == values.unset:
        return {}

    def flatten_dict(d, result=None, prv_keys=None):
        if result is None:
            result = {}

        if prv_keys is None:
            prv_keys = []

        for k, v in d.items():
            if isinstance(v, dict):
                flatten_dict(v, result, prv_keys + [k])
            else:
                result[".".join(prv_keys + [k])] = v

        return result

    if isinstance(m, dict):
        flattened = flatten_dict(m)
        return {"{}.{}".format(prefix, k): v for k, v in flattened.items()}

    return {}


def object(obj):
    """This function returns a JSON string representation of the input object if the object is JSONifiable. Otherwise, it returns the object untouched.
    Input-Output Arguments
    :param obj: Any. The input object to be converted to a JSON string.
    :return: String. The JSON string representation of the input object if it is JSONifiable, otherwise the input object itself.
    """


def map(lst, serialize_func):
    """
    Applies serialize_func to every element in lst
    """
    if not isinstance(lst, list):
        return lst
    return [serialize_func(e) for e in lst]