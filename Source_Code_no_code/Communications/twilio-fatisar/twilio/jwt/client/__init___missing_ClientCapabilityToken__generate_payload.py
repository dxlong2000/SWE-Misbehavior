from twilio.jwt import Jwt

from urllib.parse import urlencode


class ClientCapabilityToken(Jwt):
    """A token to control permissions with Twilio Client"""

    ALGORITHM = "HS256"

    def __init__(
        self,
        account_sid,
        auth_token,
        nbf=Jwt.GENERATE,
        ttl=3600,
        valid_until=None,
        **kwargs
    ):
        """
        :param str account_sid: The account sid to which this token is granted access.
        :param str auth_token: The secret key used to sign the token. Note, this auth token is not
                               visible to the user of the token.
        :param int nbf: Time in secs from epic before which this token is considered invalid.
        :param int ttl: the amount of time in seconds from generation that this token is valid for.
        :param kwargs:


        :returns: A new CapabilityToken with zero permissions
        """
        super(ClientCapabilityToken, self).__init__(
            algorithm=self.ALGORITHM,
            secret_key=auth_token,
            issuer=account_sid,
            nbf=nbf,
            ttl=ttl,
            valid_until=None,
        )

        self.account_sid = account_sid
        self.auth_token = auth_token
        self.client_name = None
        self.capabilities = {}

        if "allow_client_outgoing" in kwargs:
            self.allow_client_outgoing(**kwargs["allow_client_outgoing"])
        if "allow_client_incoming" in kwargs:
            self.allow_client_incoming(**kwargs["allow_client_incoming"])
        if "allow_event_stream" in kwargs:
            self.allow_event_stream(**kwargs["allow_event_stream"])

    def allow_client_outgoing(self, application_sid, **kwargs):
        """
        Allow the user of this token to make outgoing connections. Keyword arguments are passed
        to the application.

        :param str application_sid: Application to contact
        """
        scope = ScopeURI("client", "outgoing", {"appSid": application_sid})
        if kwargs:
            scope.add_param("appParams", urlencode(kwargs, doseq=True))

        self.capabilities["outgoing"] = scope

    def allow_client_incoming(self, client_name):
        """
        Allow the user of this token to accept incoming connections.

        :param str client_name: Client name to accept calls from
        """
        self.client_name = client_name
        self.capabilities["incoming"] = ScopeURI(
            "client", "incoming", {"clientName": client_name}
        )

    def allow_event_stream(self, **kwargs):
        """
        Allow the user of this token to access their event stream.
        """
        scope = ScopeURI("stream", "subscribe", {"path": "/2010-04-01/Events"})
        if kwargs:
            scope.add_param("params", urlencode(kwargs, doseq=True))

        self.capabilities["events"] = scope

    def _generate_payload(self):
        """This function generates the payload for the ClientCapabilityToken. It checks if the "outgoing" capability is present in the capabilities dictionary and if the client name is not None. If both conditions are met, it adds a parameter "clientName" with the value of the client name to the "outgoing" capability. Then, it creates a list of payload values on each capability in the capabilities dictionary. Finally, it returns a dictionary with a single key "scope" and the value being a string of all the scope_uris joined by a space.
        Input-Output Arguments
        :param self: ClientCapabilityToken. An instance of the ClientCapabilityToken class.
        :return: Dictionary. The generated payload for the ClientCapabilityToken.
        """


class ScopeURI(object):
    """A single capability granted to Twilio Client and scoped to a service"""

    def __init__(self, service, privilege, params=None):
        self.service = service
        self.privilege = privilege
        self.params = params or {}

    def add_param(self, key, value):
        self.params[key] = value

    def to_payload(self):
        if self.params:
            sorted_params = sorted([(k, v) for k, v in self.params.items()])
            encoded_params = urlencode(sorted_params)
            param_string = "?{}".format(encoded_params)
        else:
            param_string = ""
        return "scope:{}:{}{}".format(self.service, self.privilege, param_string)

    def __str__(self):
        return "<ScopeURI {}>".format(self.to_payload())