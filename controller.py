import webapp2
import cgi
from google.appengine.ext.webapp import template


class MainPage(webapp2.RequestHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(template.render('index.html', {}))

class SearchResponse(webapp2.RequestHandler):

    def post(self):
    	self.response.write('<html><body>You wrote:<pre>')
        self.response.write(cgi.escape(self.request.get('value')))
        self.response.write('</pre></body></html>')


application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/search', SearchResponse),
], debug=True)
