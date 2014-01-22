import webapp2

import json
import urllib2
from google.appengine.api import urlfetch

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
