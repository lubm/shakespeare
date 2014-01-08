import webapp2
from google.appengine.ext.webapp import template


class MainPage(webapp2.RequestHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        # self.render('<html><body>Hello</body></html>')
        self.response.write(template.render('index.html', {}))


application = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)
