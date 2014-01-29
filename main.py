"""Defines the application handlers"""
import webapp2

from admin_page_controller import AdminPageController
from admin_page_controller import DownloadHandler
from admin_page_controller import UploadHandler
from home_page_controller import HomePageController
from results_page_controller import ResultsPageController
from define_page_controller import DefinePageController

APP = webapp2.WSGIApplication([
    ('/', HomePageController),
    ('/search', ResultsPageController),
    ('/admin', AdminPageController),
    ('/upload', UploadHandler),
    (r'/blobstore/(.*)', DownloadHandler),
    ('/define', DefinePageController),
], debug=True)
