""" Routes for each group of actions with their handlers."""

# F:  2, 0: Unable to import 'webapp2'
# pylint: disable=F0401
import webapp2

from admin_page_controller import AdminPageController
from admin_page_controller import DownloadHandler
from admin_page_controller import UploadHandler
from create_database_controller import CreateDatabaseController
from home_page_controller import HomePageController
from main_page_controller import MainPageController
from define_page_controller import DefinePageController

application = webapp2.WSGIApplication([
    ('/define', DefinePageController),
    ('/', HomePageController),
    ('/search', MainPageController),
    ('/create_database', CreateDatabaseController),
    ('/admin', AdminPageController),
    ('/upload', UploadHandler),
    (r'/blobstore/(.*)', DownloadHandler),
], debug=True)
