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
    """This function takes a dictionary `m` and a prefix as input and returns a new dictionary with the same keys and values as `m`, but with the added prefix to the keys.
    Input-Output Arguments
    :param m: Dictionary. The input dictionary.
    :param prefix: String. The prefix to be added to the keys in the input dictionary.
    :return: Dictionary. A new dictionary with the same keys and values as the input dictionary, but with the added prefix to the keys.
    """


def object(obj):
    """
    Return a jsonified string represenation of obj if obj is jsonifiable else
    return obj untouched
    """
    if isinstance(obj, dict) or isinstance(obj, list):
        return json.dumps(obj)
    return obj


def map(lst, serialize_func):
    """
    Applies serialize_func to every element in lst
    """
    if not isinstance(lst, list):
        return lst
    return [serialize_func(e) for e in lst]