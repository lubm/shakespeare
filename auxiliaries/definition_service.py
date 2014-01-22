import json
import urllib2
from protorpc import remote
from protorpc import messages
from protorpc.transport import HttpTransport

class DefinitionRequest(messages.Message):
    """Request object used to communicate with the DefinitionService.

    Attributes:
        term: contains word to be searched. This attribute is required.
    """
    term = messages.StringField(1, required=True)

class DefinitionResponse(messages.Message):
    """Response object returned by the DefinitionService.

    Attributes:
        definition: list of
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
        """Performs an RPC call to the definition service to obtain the first 
        definiton of the word.

        Args:
            request: DefinitionRequest object containing the word to be defined 
            by the definition service.

        Returns:
            A DefinitionResponse object containing a list of definitions for the
            searched word.
        """
        return self.service.define(request)
