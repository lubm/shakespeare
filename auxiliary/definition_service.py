"""Remote definition server functionalities.

This module contains classes that are useful for using the remote
Definition Service. Contains the Request and Response objects and also the
definition service wrapper.
"""

from protorpc import messages
from protorpc import remote
from protorpc.transport import HttpTransport

class DefinitionRequest(messages.Message):
    """Request object used to communicate with the DefinitionService.

    Attributes:
        term: contains word to be searched. This attribute is required
    """
    term = messages.StringField(1, required=True)


class DefinitionResponse(messages.Message):
    """Response object returned by the DefinitionService.

    Attributes:
        definition: list of definitions for this word in the dictionary. If the
        word is not found the list will be empty.
    """
    definition = messages.StringField(1, repeated=True)


class DefinitionService(remote.Service):
    """Remote Server used to define words.

    Attributes:
        service: Definition services address.
    """
    def __init__(self):
        """DefinitionService initialization.

        Assigns the service attribute to link to the service url.
        """
        service_url = 'http://definition-server.appspot.com/definition'
        self.service = self.Stub(HttpTransport(service_url))

    @remote.method(DefinitionRequest, DefinitionResponse)
    def define(self, request):
        """Performs an RPC call to the definition service to obtain the word's
        definitons.

        Args:
            request: DefinitionRequest object containing the word to be defined
            by the definition service.

        Returns:
            A DefinitionResponse object containing a list of definitions for the
            searched word.
        """
        # TODO: Catch Failing requests and allow the user to retry.
        return self.service.define(request)
