# Copyright (c) 2006-2009 Mitch Garnaat http://garnaat.org/
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


from boto.ec2.ec2object import EC2Object


class Address(EC2Object):
    """
    Represents an EC2 Elastic IP Address

    :ivar public_ip: The Elastic IP address.
    :ivar instance_id: The instance the address is associated with (if any).
    :ivar domain: Indicates whether the address is a EC2 address or a VPC address (standard|vpc).
    :ivar allocation_id: The allocation ID for the address (VPC addresses only).
    :ivar association_id: The association ID for the address (VPC addresses only).
    :ivar network_interface_id: The network interface (if any) that the address is associated with (VPC addresses only).
    :ivar network_interface_owner_id: The owner IID (VPC addresses only).
    :ivar private_ip_address: The private IP address associated with the Elastic IP address (VPC addresses only).
    """

    def __init__(self, connection=None, public_ip=None, instance_id=None):
        super(Address, self).__init__(connection)
        self.connection = connection
        self.public_ip = public_ip
        self.instance_id = instance_id
        self.domain = None
        self.allocation_id = None
        self.association_id = None
        self.network_interface_id = None
        self.network_interface_owner_id = None
        self.private_ip_address = None

    def __repr__(self):
        return 'Address:%s' % self.public_ip

    def endElement(self, name, value, connection):
        if name == 'publicIp':
            self.public_ip = value
        elif name == 'instanceId':
            self.instance_id = value
        elif name == 'domain':
            self.domain = value
        elif name == 'allocationId':
            self.allocation_id = value
        elif name == 'associationId':
            self.association_id = value
        elif name == 'networkInterfaceId':
            self.network_interface_id = value
        elif name == 'networkInterfaceOwnerId':
            self.network_interface_owner_id = value
        elif name == 'privateIpAddress':
            self.private_ip_address = value
        else:
            setattr(self, name, value)

    def release(self, dry_run=False):
        """
        Free up this Elastic IP address.
        :see: :meth:`boto.ec2.connection.EC2Connection.release_address`
        """
        if self.allocation_id:
            return self.connection.release_address(
                allocation_id=self.allocation_id,
                dry_run=dry_run)
        else:
            return self.connection.release_address(
                public_ip=self.public_ip,
                dry_run=dry_run
            )

    delete = release

    def associate(self, instance_id=None, network_interface_id=None, private_ip_address=None, allow_reassociation=False, dry_run=False):
        """Associate this Elastic IP address with a currently running instance. If the address has an allocation ID, it uses the allocation ID. Otherwise, it does not use the allocation ID.
        Input-Output Arguments
        :param self: Address. An instance of the Address class.
        :param instance_id: String. The ID of the instance to associate the Elastic IP address with.
        :param network_interface_id: String. The ID of the network interface to associate the Elastic IP address with.
        :param private_ip_address: String. The private IP address to associate with the Elastic IP address.
        :param allow_reassociation: Bool. Whether to allow reassociation of the Elastic IP address.
        :param dry_run: Bool. Whether to perform a dry run of the association.
        :return: The result of the association operation.
        """

    def disassociate(self, dry_run=False):
        """
        Disassociate this Elastic IP address from a currently running instance.
        :see: :meth:`boto.ec2.connection.EC2Connection.disassociate_address`
        """
        if self.association_id:
            return self.connection.disassociate_address(
                association_id=self.association_id,
                dry_run=dry_run
            )
        else:
            return self.connection.disassociate_address(
                public_ip=self.public_ip,
                dry_run=dry_run
            )