def is_node(value):
    return value in ("node", "element")


def is_shape(value):
    return value in ("shape", "exact")


def collect_array(a_value, base, nodes):
    a_type = a_value["name"]
    if is_node(a_type):
        nodes.append(base)
    elif a_type in ("shape", "exact"):
        nodes = collect_nodes(a_value["value"], base + "[]", nodes)
    elif a_type == "union":
        nodes = collect_union(a_value["value"], base + "[]", nodes)
    elif a_type == "objectOf":
        nodes = collect_object(a_value["value"], base + "[]", nodes)
    return nodes


def collect_union(type_list, base, nodes):
    for t in type_list:
        if is_node(t["name"]):
            nodes.append(base)
        elif is_shape(t["name"]):
            nodes = collect_nodes(t["value"], base, nodes)
        elif t["name"] == "arrayOf":
            nodes = collect_array(t["value"], base, nodes)
        elif t["name"] == "objectOf":
            nodes = collect_object(t["value"], base, nodes)
    return nodes


def collect_object(o_value, base, nodes):
    o_name = o_value.get("name")
    o_key = base + "{}"
    if is_node(o_name):
        nodes.append(o_key)
    elif is_shape(o_name):
        nodes = collect_nodes(o_value.get("value", {}), o_key, nodes)
    elif o_name == "union":
        nodes = collect_union(o_value.get("value"), o_key, nodes)
    elif o_name == "arrayOf":
        nodes = collect_array(o_value, o_key, nodes)
    return nodes


def collect_nodes(metadata, base="", nodes=None):
    """This function collects all the nodes in the metadata dictionary and returns them as a list. It recursively traverses the metadata dictionary and checks the type of each value to determine if it is a node, an array, a shape, a union, or an object. It appends the corresponding keys to the nodes list.
    Input-Output Arguments
    :param metadata: Dictionary. The metadata dictionary containing the nodes.
    :param base: String. The base key to be used for nested nodes. Defaults to an empty string.
    :param nodes: List. The list to store the collected nodes. Defaults to an empty list.
    :return: List. The list of collected nodes.
    """


def filter_base_nodes(nodes):
    return [n for n in nodes if not any(e in n for e in ("[]", ".", "{}"))]