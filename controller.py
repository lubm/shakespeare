import webapp2
from google.appengine.ext.webapp import template

class MainPage(webapp2.RequestHandler):

    def get(self):
    	searched_value = self.request.get('searched_word')

    	value = searched_value if searched_value is not None else ''

    	template_values = {
            'searched_word': value,
        }

        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write(template.render('index.html', template_values))


class HomePage(webapp2.RequestHandler):

	def get(self):
		self.response.headers['Content-Type'] = 'text/html'
		self.response.out.write(template.render('homepage.html', {}))


application = webapp2.WSGIApplication([
    ('/', HomePage),
    ('/search', MainPage),
], debug=True)
