import webapp2
from auxiliaries.definition_service import DefinitionService
from auxiliaries.definition_service import DefinitionRequest

class DefinePageController(webapp2.RequestHandler):
    """Handler for Definition features.

    This class contains all the logic for defining a word.

    Attributes:
        request and response are inherited from webapp2.RequestHandler.
    """

    def get(self):
        """Obtains the definion of the searched word.

        Gets the searched word from the request and calls the DefinitionService
        in order to obtain its definion. Returns the result as plain text.
        """
        definition_request = DefinitionRequest()
        definition_request.term = self.request.get('searched_word')

        definition_service = DefinitionService()
        definition_response = definition_service.define(definition_request)
        word_first_definition = definition_response.definition[0]

        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write(word_first_definition)
