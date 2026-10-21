"""
Provide urlresolver functions that return fully qualified URLs or view names
"""
from django.urls import NoReverseMatch
from django.urls import reverse as django_reverse
from django.utils.functional import lazy

from rest_framework.settings import api_settings
from rest_framework.utils.urls import replace_query_param


def preserve_builtin_query_params(url, request=None):
    """
    Given an incoming request, and an outgoing URL representation,
    append the value of any built-in query parameters.
    """
    if request is None:
        return url

    overrides = [
        api_settings.URL_FORMAT_OVERRIDE,
    ]

    for param in overrides:
        if param and (param in request.GET):
            value = request.GET[param]
            url = replace_query_param(url, param, value)

    return url


def reverse(viewname, args=None, kwargs=None, request=None, format=None, **extra):
    """This function is used to reverse a viewname into a URL. If versioning is being used, the function passes the reverse call to the versioning scheme instance to modify the resulting URL if needed.
    Input-Output Arguments
    :param viewname: The name of the view to reverse. Default to None.
    :param args: List. Positional arguments to be passed to the view. Default to None.
    :param kwargs: Dict. Keyword arguments to be passed to the view. Default to None.
    :param request: HttpRequest. The current request being processed. Default to None.
    :param format: String. The format of the URL. Default to None.
    :param extra: Dict. Extra keyword arguments to be passed to the view.
    :return: String. The reversed URL.
    """


def _reverse(viewname, args=None, kwargs=None, request=None, format=None, **extra):
    """
    Same as `django.urls.reverse`, but optionally takes a request
    and returns a fully qualified URL, using the request to get the base URL.
    """
    if format is not None:
        kwargs = kwargs or {}
        kwargs['format'] = format
    url = django_reverse(viewname, args=args, kwargs=kwargs, **extra)
    if request:
        return request.build_absolute_uri(url)
    return url


reverse_lazy = lazy(reverse, str)