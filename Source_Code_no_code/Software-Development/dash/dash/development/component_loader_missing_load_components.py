import collections
import json
import os

from ._py_components_generation import generate_class



def _get_metadata(metadata_path):
    # Start processing
    with open(metadata_path, encoding="utf-8") as data_file:
        json_string = data_file.read()
        data = json.JSONDecoder(object_pairs_hook=collections.OrderedDict).decode(
            json_string
        )
    return data


def load_components(metadata_path, namespace="default_namespace"):
    """This function loads React component metadata from a JSON file and converts it into a format that Dash can parse. It registers the component library for index inclusion and then iterates over each component in the metadata, extracting the component name and generating a class for each component. The generated classes are added to a list and returned.
    Input-Output Arguments
    :param metadata_path: String. The path to the JSON file created by `react-docgen`.
    :param namespace: String. The namespace to register the component library under. It defaults to "default_namespace" if not specified.
    :return: List of component objects. Each component object has keys `type`, `valid_kwargs`, and `setup`.
    """


def generate_classes(namespace, metadata_path="lib/metadata.json"):
    """Load React component metadata into a format Dash can parse, then create
    Python class files.

    Usage: generate_classes()

    Keyword arguments:
    namespace -- name of the generated Python package (also output dir)

    metadata_path -- a path to a JSON file created by
    [`react-docgen`](https://github.com/reactjs/react-docgen).

    Returns:
    """

    from ._py_components_generation import generate_imports
    from ._py_components_generation import generate_class_file
    from ._py_components_generation import generate_classes_files
    data = _get_metadata(metadata_path)
    imports_path = os.path.join(namespace, "_imports_.py")

    # Make sure the file doesn't exist, as we use append write
    if os.path.exists(imports_path):
        os.remove(imports_path)

    components = generate_classes_files(namespace, data, generate_class_file)

    # Add the __all__ value so we can import * from _imports_
    generate_imports(namespace, components)