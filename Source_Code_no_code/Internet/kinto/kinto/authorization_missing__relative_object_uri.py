from pyramid.interfaces import IAuthorizationPolicy
from zope.interface import implementer

from kinto.core import authorization as core_authorization

# Vocab really matters when you deal with permissions. Let's do a quick recap
# of the terms used here:
#
# Object URI:
#    An unique identifier for an object.
#    for instance, /buckets/blog/collections/articles/records/article1
#
# Object:
#    A common denomination of an object (e.g. "collection" or "record")
#
# Unbound permission:
#    A permission not bound to an object (e.g. "create")
#
# Bound permission:
#    A permission bound to an object (e.g. "collection:create")


# Dictionary that associates single permissions to any other permission that
# automatically provides it
# Ex: bucket:read is granted by both bucket:write and bucket:read
PERMISSIONS_INHERITANCE_TREE = {
    "root": {"bucket:create": {}, "write": {}, "read": {}},  # Granted via settings only.
    "bucket": {
        "write": {"bucket": ["write"]},
        "read": {"bucket": ["write", "read"]},
        "read:attributes": {"bucket": ["write", "read", "collection:create", "group:create"]},
        "group:create": {"bucket": ["write", "group:create"]},
        "collection:create": {"bucket": ["write", "collection:create"]},
    },
    "group": {
        "write": {"bucket": ["write"], "group": ["write"]},
        "read": {"bucket": ["write", "read"], "group": ["write", "read"]},
    },
    "collection": {
        "write": {"bucket": ["write"], "collection": ["write"]},
        "read": {"bucket": ["write", "read"], "collection": ["write", "read"]},
        "read:attributes": {
            "bucket": ["write", "read"],
            "collection": ["write", "read", "record:create"],
        },
        "record:create": {"bucket": ["write"], "collection": ["write", "record:create"]},
    },
    "record": {
        "write": {"bucket": ["write"], "collection": ["write"], "record": ["write"]},
        "read": {
            "bucket": ["write", "read"],
            "collection": ["write", "read"],
            "record": ["write", "read"],
        },
    },
}


def _resource_endpoint(object_uri):
    """Determine the resource name and whether it is the plural endpoint from
    the specified `object_uri`. Returns `(None, None)` for the root URL plural
    endpoint.
    """
    obj_parts = object_uri.split("/")
    plural_endpoint = len(obj_parts) % 2 == 0
    if plural_endpoint:
        # /buckets/bid/collections -> /buckets/bid
        obj_parts = obj_parts[:-1]

    if len(obj_parts) <= 2:
        # Root URL /buckets -> ('', False)
        return "", False

    # /buckets/bid -> buckets
    resource_name = obj_parts[-2]
    # buckets -> bucket
    resource_name = resource_name.rstrip("s")
    return resource_name, plural_endpoint


def _relative_object_uri(resource_name, object_uri):
    """This function takes a resource name and an object URI as input and returns the object URI. It splits the object URI into parts and iterates through each part to find the parent URI. It then checks if the resource name matches the parent resource name. If a match is found, it returns the parent URI. If no match is found, it raises a ValueError with an error message.
    Input-Output Arguments
    :param resource_name: String. The name of the resource.
    :param object_uri: String. The URI of the object.
    :return: String. The object URI.
    """


def _inherited_permissions(object_uri, permission):
    """Build the list of all permissions that can grant access to the given
    object URI and permission.

    >>> _inherited_permissions('/buckets/blog/collections/article', 'read')
    [('/buckets/blog/collections/article', 'write'),
     ('/buckets/blog/collections/article', 'read'),
     ('/buckets/blog', 'write'),
     ('/buckets/blog', 'read')]

    """
    resource_name, plural = _resource_endpoint(object_uri)
    try:
        object_perms_tree = PERMISSIONS_INHERITANCE_TREE[resource_name]
    except KeyError:
        return []  # URL that are not resources have no inherited perms.

    # When requesting permissions for a single object, we check if they are any
    # specific inherited permissions for the attributes.
    attributes_permission = f"{permission}:attributes" if not plural else permission
    inherited_perms = object_perms_tree.get(attributes_permission, object_perms_tree[permission])

    granters = set()
    for related_resource_name, implicit_permissions in inherited_perms.items():
        for permission in implicit_permissions:
            related_uri = _relative_object_uri(related_resource_name, object_uri)
            granters.add((related_uri, permission))

    # Sort by ascending URLs.
    return sorted(granters, key=lambda uri_perm: len(uri_perm[0]), reverse=True)


@implementer(IAuthorizationPolicy)
class AuthorizationPolicy(core_authorization.AuthorizationPolicy):
    def get_bound_permissions(self, *args, **kwargs):
        return _inherited_permissions(*args, **kwargs)


class RouteFactory(core_authorization.RouteFactory):
    pass