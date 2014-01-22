
import webapp2
from google.appengine.api import urlfetch


from admin_page_controller import AdminPageController
from admin_page_controller import DownloadHandler
from admin_page_controller import UploadHandler
from create_database_controller import CreateDatabaseController
from home_page_controller import HomePageController
from main_page_controller import MainPageController


class DefinePage(webapp2.RequestHandler):

    def get(self):
        rpc = urlfetch.create_rpc()
        urlfetch.make_fetch_call(rpc, "http://definition-server.appspot.com/definition.define")


application = webapp2.WSGIApplication([
    ('/', HomePageController),
    ('/search', MainPageController),
    ('/create_database', CreateDatabaseController),
    ('/admin', AdminPageController),
    ('/upload', UploadHandler),
    (r'/blobstore/(.*)', DownloadHandler),
], debug=True)
