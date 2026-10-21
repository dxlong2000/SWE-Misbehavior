########################################################################
# File name: service.py
# This file is part of: aioxmpp
#
# LICENSE
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program.  If not, see
# <http://www.gnu.org/licenses/>.
#
########################################################################
import asyncio

import aioxmpp
import aioxmpp.service as service

from . import xso as vcard_xso


class VCardService(service.Service):
    """
    Service for handling vcard-temp.

    .. automethod:: get_vcard

    .. automethod:: set_vcard
    """

    async def get_vcard(self, jid=None):
        """
        Get the vCard stored for the jid `jid`. If `jid` is
        :data:`None` get the vCard of the connected entity.

        :param jid: the object to retrieve.
        :returns: the stored vCard.

        We mask a :class:`XMPPCancelError` in case it is
        ``feature-not-implemented`` or ``item-not-found`` and return
        an empty vCard, since this can be understood to be semantically
        equivalent.
        """

        iq = aioxmpp.IQ(
            type_=aioxmpp.IQType.GET,
            to=jid,
            payload=vcard_xso.VCard(),
        )

        try:
            return await self.client.send(iq)
        except aioxmpp.XMPPCancelError as e:
            if e.condition in (
                    aioxmpp.ErrorCondition.FEATURE_NOT_IMPLEMENTED,
                    aioxmpp.ErrorCondition.ITEM_NOT_FOUND):
                return vcard_xso.VCard()
            else:
                raise

    async def set_vcard(self, vcard, jid=None):
        """This function stores the vCard `vcard` for the connected entity. It creates an IQ instance with the vCard payload and sends it to the client.
        Input-Output Arguments
        :param self: VCardService. An instance of the VCardService class.
        :param vcard: The vCard to store.
        :param jid: The JID to which the vCard is to be stored. Defaults to None.
        :return: No return value.
        """