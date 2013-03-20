import os
from formbar.helpers import get_css


def get_path_to(location):
    """Will return the full pathname the given file name with in the path. path
    is relativ to the ringo package root."""
    return os.path.join(os.path.dirname(
                        os.path.abspath(__file__)), '..', location)


def get_path_to_form_config(filename):
    """Returns the path the the given form configuration. The file name
    should be realtive to the default location for the configurations.

    :file: filename
    :returns: Absolute path to the configuration file

    """
    location = "views/forms"
    return get_path_to(os.path.join(location, filename))


def get_formbar_css():
    return get_css()
