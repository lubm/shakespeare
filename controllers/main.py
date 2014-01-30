"""Defines the application handlers"""
import webapp2

from controllers.admin_page import AdminPageController
from controllers.admin_page import ClearDatastoreHandler
from controllers.admin_page import DownloadHandler
from controllers.admin_page import UploadHandler
from controllers.home_page import HomePageController
from controllers.results_page import ResultsPageController
from controllers.define_page import DefinePageController

APP = webapp2.WSGIApplication([
    ('/', HomePageController),
    ('/search', ResultsPageController),
    ('/admin', AdminPageController),
    ('/upload', UploadHandler),
    (r'/blobstore/(.*)', DownloadHandler),
    ('/define', DefinePageController),
    ('/clear', ClearDatastoreHandler),
], debug=True)