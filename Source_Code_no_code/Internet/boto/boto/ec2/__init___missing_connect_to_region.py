# Copyright (c) 2006-2008 Mitch Garnaat http://garnaat.org/
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
"""
This module provides an interface to the Elastic Compute Cloud (EC2)
service from AWS.
"""
from boto.ec2.connection import EC2Connection
from boto.regioninfo import get_regions, load_regions



RegionData = load_regions().get('ec2', {})


def regions(**kw_params):
    """
    Get all available regions for the EC2 service.
    You may pass any of the arguments accepted by the EC2Connection
    object's constructor as keyword arguments and they will be
    passed along to the EC2Connection object.

    :rtype: list
    :return: A list of :class:`boto.ec2.regioninfo.RegionInfo`
    """
    return get_regions('ec2', connection_cls=EC2Connection)


def connect_to_region(region_name, **kw_params):
    """This function connects to a specific region and returns an EC2Connection object.
    Input-Output Arguments
    :param region_name: str. The name of the region to connect to.
    :param **kw_params: Additional parameters that are passed on to the connect method of the region object.
    :return: EC2Connection or None. A connection to the given region, or None if an invalid region name is given.
    """


def get_region(region_name, **kw_params):
    """
    Find and return a :class:`boto.ec2.regioninfo.RegionInfo` object
    given a region name.

    :type: str
    :param: The name of the region.

    :rtype: :class:`boto.ec2.regioninfo.RegionInfo`
    :return: The RegionInfo object for the given region or None if
             an invalid region name is provided.
    """
    for region in regions(**kw_params):
        if region.name == region_name:
            return region
    return None