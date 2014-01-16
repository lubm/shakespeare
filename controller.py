
import webapp2
from google.appengine.api import urlfetch


from main_page_controller import MainPageController
from home_page_controller import HomePageController
from create_database_controller import CreateDatabaseController


class DefinePage(webapp2.RequestHandler):

    def get(self):
        rpc = urlfetch.create_rpc()
        urlfetch.make_fetch_call(rpc, "http://definition-server.appspot.com/definition.define")


application = webapp2.WSGIApplication([
    ('/', HomePageController),
    ('/search', MainPageController),
    ('/create_database', CreateDatabaseController)
], debug=True)
