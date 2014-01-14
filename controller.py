import cgi

import time
import webapp2
from google.appengine.ext.webapp import template

from models.mention import Mention
from models.word import Word
from tasks.parser import Parser

class MainPage(webapp2.RequestHandler):

    def get(self):
    	searched_value = self.request.get('searched_word')

    	value = searched_value if searched_value else ''
        
        mentions = []
        if value:
            start = time.time()
            word = Word.get_from_index(cgi.escape(value))
            end = time.time()
            if word:
                mentions = word.mentions


    	template_values = {
            'searched_word': value,
            'mentions_list': mentions,
            'number_results': len(mentions),
            'time': round(end-start, 4)
        }
        print mentions

        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write(template.render('index.html', template_values))


class HomePage(webapp2.RequestHandler):

	def get(self):
		self.response.headers['Content-Type'] = 'text/html'
		self.response.out.write(template.render('homepage.html', {}))


class CreateDatabase(webapp2.RequestHandler):

    def get(self):
        parser = Parser('test_data')
        parser.parse()

        self.redirect('/')
    
application = webapp2.WSGIApplication([
    ('/', HomePage),
    ('/search', MainPage),
    ('/create_database', CreateDatabase)
], debug=True)
