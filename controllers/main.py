"""Defines the application routing"""
import webapp2

from controllers.admin_page import AdminPageController
from controllers.admin_page import ClearDatastoreHandler
from controllers.admin_page import DownloadHandler
from controllers.admin_page import UploadHandler
from controllers.home_page import HomePageController
from controllers.results_page import ResultsPageController
from controllers.define_page import DefinePageController
from controllers.results_page import TreemapHandler
from controllers.results_page import CharactersHandler
from controllers.results_page import FilterHandler

APP = webapp2.WSGIApplication([
    ('/', HomePageController),
    ('/search', ResultsPageController),
    ('/admin', AdminPageController),
    ('/upload', UploadHandler),
    (r'/blobstore/(.*)', DownloadHandler),
    ('/define', DefinePageController),
    ('/clear', ClearDatastoreHandler),
    ('/treemap', TreemapHandler),
    ('/chars', CharactersHandler),
    ('/filter', FilterHandler)
], debug=True)

