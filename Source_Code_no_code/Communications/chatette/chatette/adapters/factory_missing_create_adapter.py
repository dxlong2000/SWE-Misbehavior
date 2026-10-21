"""
Module `chatette.adapters.factory`.
Defines a factory method that allows to create an adapter from a string name.
"""






def create_adapter(adapter_name, base_filepath=None):
    """This function creates and returns an instance of an adapter based on the given adapter name. The adapter names are used to determine which adapter class to instantiate. The mames are the following format:'rasa','rasa-md' or 'rasamd','jsonl'.
    Input-Output Arguments
    :param adapter_name: String. The name of the adapter to be instantiated.
    :param base_filepath: String. The base file path to be used by the adapter. Defaults to None.
    :return: Adapter. The instantiated adapter instance based on the given adapter name.
    """