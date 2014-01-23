import unittest

from auxiliary.definition_service import DefinitionService
from auxiliary.definition_service import DefinitionRequest

class DefineServiceTest(unittest.TestCase):
    """Tests for the DefinitionService wrapper"""

    def setUp(self):
        self.definition_service = DefinitionService()
        self.definition_request = DefinitionRequest()

    def test_search_an_empty_word(self):
        self.definition_request.term = ''
        definition_response = self.definition_service.define(
            self.definition_request)
        self.assertEqual(definition_response.definition, [])

    def test_search_a_not_found_word(self):
        self.definition_request.term = 'fsfsdf'
        definition_response = self.definition_service.define(
            self.definition_request)
        self.assertEqual(definition_response.definition, [])

    def test_search_word(self):
        self.definition_request.term = 'friend'
        definition_response = self.definition_service.define(
            self.definition_request)
        self.assertIn(
            'a person you know well and regard with affection and trust',
            definition_response.definition)
        self.assertIn('an associate who provides cooperation or assistance',
            definition_response.definition)


if __name__ == '__main__':
    unittest.main()
