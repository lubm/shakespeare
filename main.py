"""Defines the application handlers"""
import webapp2

from admin_page_controller import AdminPageController
from admin_page_controller import DownloadHandler
from admin_page_controller import UploadHandler
from create_database_controller import CreateDatabaseController
from home_page_controller import HomePageController
from main_page_controller import MainPageController


APP = webapp2.WSGIApplication([
    ('/', HomePageController),
    ('/search', MainPageController),
    ('/admin', AdminPageController),
    ('/upload', UploadHandler),
    (r'/blobstore/(.*)', DownloadHandler),
], debug=True)
