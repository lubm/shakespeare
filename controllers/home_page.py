"""Module for the home page rendering"""
import webapp2

from google.appengine.ext.webapp import template


class HomePageController(webapp2.RequestHandler):
    """Class for handling home page requests"""
    def get(self):
        """Renders the home page"""
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write(template.render('templates/homepage.html', {}))
