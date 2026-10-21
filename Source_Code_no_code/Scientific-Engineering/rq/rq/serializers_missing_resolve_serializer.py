import json
import pickle
from functools import partial
from typing import Optional, Type, Union




class DefaultSerializer:
    dumps = partial(pickle.dumps, protocol=pickle.HIGHEST_PROTOCOL)
    loads = pickle.loads


class JSONSerializer:
    @staticmethod
    def dumps(*args, **kwargs):
        return json.dumps(*args, **kwargs).encode('utf-8')

    @staticmethod
    def loads(s, *args, **kwargs):
        return json.loads(s.decode('utf-8'), *args, **kwargs)


def resolve_serializer(serializer: Optional[Union[Type[DefaultSerializer], str]] = None) -> Type[DefaultSerializer]:
    """This function checks the user-defined serializer for the presence of 'dumps' and 'loads' methods. If these methods are not found, it raises a NotImplementedError. If the serializer is not provided, it returns the default pickle serializer. If a string path to a serializer is provided, it loads and returns that serializer. The returned serializer objects implement the 'dumps' and 'loads' methods.
    Input-Output Arguments
    :param serializer: Optional. Union of Type[DefaultSerializer] and str. The serializer to resolve. Defaults to None.
    :return: Type[DefaultSerializer]. An object that implements the SerializerProtocol.
    """