import plaster


def parse_vars(args):
    """This function takes a list of strings in the format 'a=b' and turns it into a dictionary with keys and values.
    Input-Output Arguments
    :param args: List of strings. The list of strings in the format 'a=b'.
    :return: Dictionary. The dictionary with keys and values.
    """


def get_config_loader(config_uri):
    """
    Find a ``plaster.ILoader`` object supporting the "wsgi" protocol.

    """
    return plaster.get_loader(config_uri, protocols=['wsgi'])