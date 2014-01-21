
import webapp2
from google.appengine.api import urlfetch


from admin_page_controller import AdminPageController
from admin_page_controller import UploadHandler
from create_database_controller import CreateDatabaseController
from home_page_controller import HomePageController
from main_page_controller import MainPageController

import json
import urllib2

class DefinePageController(webapp2.RequestHandler):

    def get(self):
        searched_value = self.request.get('searched_word')
        values = {
            'term' : searched_value,
        }
        req = urllib2.Request("http://definition-server.appspot.com/definition.define")
        req.add_header('Content-Type', 'application/json')
        rpc_response = urllib2.urlopen(req, json.dumps(values))

        self.response.headers['Content-Type'] = 'text/plain'        
        self.response.out.write(rpc_response.read())

        
application = webapp2.WSGIApplication([
    ('/define', DefinePageController),
    ('/', HomePageController),
    ('/search', MainPageController),
    ('/create_database', CreateDatabaseController),
    ('/admin', AdminPageController),
    ('/upload', UploadHandler),
], debug=True)
