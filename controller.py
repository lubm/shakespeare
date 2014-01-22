import webapp2

from admin_page_controller import AdminPageController
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
], debug=True)
