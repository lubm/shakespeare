import webapp2
from auxiliary.parser import Parser

class CreateDatabaseController(webapp2.RequestHandler):

    def get(self):
        parser = Parser('test_data')
        parser.parse()

        self.redirect('/')
