import cgi
import re

import webapp2
from google.appengine.ext.webapp import template

from models.mention import Mention
from models.word import Word
from tasks.parser import Parser

class MainPage(webapp2.RequestHandler):

    def get(self):
    	searched_value = self.request.get('searched_word')

    	value = searched_value if searched_value else ''

        work_mentions = []
        if value:
            word = Word.get_from_index(cgi.escape(value))
            if word:
                # Grouping mentions by work for UI display
                work_mentions = {}               
                for mention in word.mentions:
                    # Making the words stay bold
                    line = re.sub(value, "<b>%s</b>" % value, mention.line)
                    if mention.work not in work_mentions:
                        work_mentions[mention.work] = []
                    work_mentions[mention.work].append(line)

        print work_mentions
        if work_mentions:
            print "------not empty"
        for work in work_mentions:
            print work

    	template_values = {
            'searched_word': value,
            'work_mentions': work_mentions
        }

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
