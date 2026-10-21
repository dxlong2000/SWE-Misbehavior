"""
The Python module allows you to execute Python code within the context of a deploy.
"""

from inspect import getfullargspec


from pyinfra.api import FunctionCommand, operation



@operation(is_idempotent=False)
def call(function, *args, **kwargs):
    """This function executes a Python function within a deploy. It takes a function, along with its arguments and keyword arguments, and yields a FunctionCommand object.
    Input-Output Arguments
    :param function: The Python function to execute.
    :param args: The arguments to pass to the function.
    :param kwargs: The keyword arguments to pass to the function.
    :return: A FunctionCommand object.
    """


@operation(is_idempotent=False)
def raise_exception(exception, *args, **kwargs):
    """
    Raise a Python exception within a deploy.

    + exception: the exception class to raise
    + args: arguments passed to the exception creation
    + kwargs: keyword arguments passed to the exception creation

    **Example**:

    .. code:: python

        python.raise_exception(
            name="Raise NotImplementedError exception",
            exception=NotImplementedError,
            message="This is not implemented",
        )
    """

    def raise_exc(*args, **kwargs):  # pragma: no cover
        raise exception(*args, **kwargs)

    kwargs.pop("state", None)
    kwargs.pop("host", None)
    yield FunctionCommand(raise_exc, args, kwargs)