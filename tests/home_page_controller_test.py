import webtest
import unittest
import webapp2
from controllers.home_page import HomePageController

"""Run this tests like this:
nosetests --with-gae tests/home_page_controller_test.py """

# Disable Too many public methods warning
# pylint: disable=R0904
class HomePageControllerTest(unittest.TestCase):
    """Tests for the handler of the home page."""

    def setUp(self):
        """Create the dummy webapp."""
        app = webapp2.WSGIApplication([('/', HomePageController)])
        self.testapp = webtest.TestApp(app)

    def test_get_home_page(self):
        """Load the home page"""
        response = self.testapp.get('/')
        self.assertEqual(response.status_int, 200)
        self.assertTrue('Enter word' in response.normal_body)
        self.assertTrue('Search' in response.normal_body)
