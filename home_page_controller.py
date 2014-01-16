import webapp2
from google.appengine.ext.webapp import template


class HomePageController(webapp2.RequestHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write(template.render('templates/homepage.html', {}))
