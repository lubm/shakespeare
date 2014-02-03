import webtest
from controllers.define_page import DefinePageController
import unittest
import  webapp2

"""Run this tests like this:
nosetests --with-gae tests/define_page_controller_test.py """

# Disable Too many public methods warning
# pylint: disable=R0904
class DefinePageControllerTest(unittest.TestCase):
    """Tests for the handler of the definition service"""

    def setUp(self):
        """Create the dummy webapp"""
        app = webapp2.WSGIApplication([('/define', DefinePageController)])
        self.testapp = webtest.TestApp(app)

    def test_get_definition(self):
        """Search a word that is found"""
        response = self.testapp.get('/define?searched_word=Friend')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.normal_body,
            'a person you know well and regard with affection and trust')
        self.assertEqual(response.content_type, 'text/plain')

    def test_define_invalid_word(self):
        """Search a word that is not found"""
        response = self.testapp.get('/define?searched_word=asts')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.normal_body,
            'Word not found in the dictionary')
        self.assertEqual(response.content_type, 'text/plain')
