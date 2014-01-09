import webapp2
import cgi
from google.appengine.ext.webapp import template

class MainPage(webapp2.RequestHandler):

    def get(self):
    	searched_value = self.response.write(cgi.escape(self.request.get('value')))

        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(template.render('index.html', {'value' : searched_value}))


class HomePage(webapp2.RequestHandler):

	def get(self):
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(template.render('homepage.html', {}))


application = webapp2.WSGIApplication([
    ('/', HomePage),
    ('/search', MainPage),
], debug=True)
