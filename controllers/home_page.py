"""Module for the home page rendering"""
import webapp2
from resources.constants import Constants

class HomePageController(webapp2.RequestHandler):
    """Class for handling home page requests"""
    def get(self):
        """Renders the home page"""
        template = Constants.JINJA_ENVIRONMENT.get_template('homepage.html')
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(template.render())
