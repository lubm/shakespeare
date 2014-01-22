import json
import urllib2

class DefinitionService(object):
    """Definition Ser
    """
    def __init__(self):
        self.service_url = "http://definition-server.appspot.com/definition.define"

    def define(self, searched_value):
        values = {
            'term' : searched_value,
        }
        req = urllib2.Request(self.service_url)
        req.add_header('Content-Type', 'application/json')
        return urllib2.urlopen(req, json.dumps(values)).read()
