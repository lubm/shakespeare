import webapp2

from auxiliary.definition_service import DefinitionService
from auxiliary.definition_service import DefinitionRequest

class DefinePageController(webapp2.RequestHandler):
    """Handler for Definition features.

    This class contains all the logic for defining a word.

    Attributes:
        request and response are inherited from webapp2.RequestHandler.
    """

    def get(self):
        """Obtains the definion of the searched word.

        Gets the searched word from the request and calls the DefinitionService
        in order to obtain its definion.

        Returns:
            The first definition of the word if it is found in the dictionary or
            an 'Word not found' message. All results are returned as plain text.
        """
        definition_request = DefinitionRequest()
        definition_request.term = self.request.get('searched_word')

        definition_service = DefinitionService()
        definition_response = definition_service.define(definition_request)

        if len(definition_response.definition) > 0:
            result = definition_response.definition[0]
        else:
            result = 'Word not found in the dictionary'

        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write(result)
