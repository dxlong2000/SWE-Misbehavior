import gettext
import os
from importlib import import_module

PATH = '{0}.py'.format(os.path.splitext(__file__)[0])
DOMAIN = 'mssql-cli'
LOCALE_DIR = os.path.join(os.path.dirname(__file__), 'locale')
LANGUAGES = None

def translation(domain=DOMAIN, localedir=LOCALE_DIR, languages=None):
    """This function creates a translation object based on the given parameters. It uses the gettext module to load translations from the specified domain and localedir for the specified languages. If languages is not provided, it uses the default LANGUAGES.
    Input-Output Arguments
    :param domain: String. The translation domain to load translations from. It defaults to DOMAIN if not specified.
    :param localedir: String. The directory where translation files are located. It defaults to LOCALE_DIR if not specified.
    :param languages: List of strings. The languages for which translations should be loaded. It defaults to LANGUAGES if not specified.
    :return: Translation object. The created translation object.
    """

translation().install()


## Localized Strings
def goodbye():
    return _(u'Goodbye!')