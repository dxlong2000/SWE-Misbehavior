# Copyright (c) 2015 Amazon.com, Inc. or its affiliates.
# All Rights Reserved
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
from boto.regioninfo import get_regions



def regions():
    """
    Get all available regions for the Amazon EC2 Container Service.

    :rtype: list
    :return: A list of :class:`boto.regioninfo.RegionInfo`
    """
    from boto.ec2containerservice.layer1 import EC2ContainerServiceConnection
    return get_regions('ec2containerservice',
                       connection_cls=EC2ContainerServiceConnection)


def connect_to_region(region_name, **kw_params):
    """Connect to a specific region using the EC2ContainerServiceConnection class from the boto library. It creates an instance of the EC2ContainerServiceConnection class with the specified region name and additional keyword parameters.
    Input-Output Arguments
    :param region_name: String. The name of the region to connect to.
    :param **kw_params: Additional keyword parameters that can be passed to the EC2ContainerServiceConnection class.
    :return: EC2ContainerServiceConnection. An instance of the EC2ContainerServiceConnection class connected to the specified region.
    """