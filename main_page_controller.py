import cgi

from google.appengine.ext.webapp import template

import re
import webapp2
import time

from models.word import Word

class MainPageController(webapp2.RequestHandler):

    def get(self):
        searched_value = self.request.get('searched_word')

        value = searched_value.lower() if searched_value else ''

        work_mentions = []
        number_results = 0
        if value:
            start = time.time()
            word = Word.get_from_shakespeare_index(cgi.escape(value))
            end = time.time()
            if word:
                # Grouping mentions by work for UI display
                work_mentions = {}
                regex = ''
                for letter in word.name:
                    regex += '[' + letter + letter.upper() + ']'
                for mention in word.mentions:
                    number_results += 1
                    # Making the words stay bold
                    line = mention.line
                    matches = re.findall(regex, line)
                    for match in matches:
                        line = re.sub(match, '<b>%s</b>' % match, line)
                    if mention.work not in work_mentions:
                        work_mentions[mention.work] = []
                    work_mentions[mention.work].append(line)

        template_values = {
            'searched_word': value,
            'work_mentions': work_mentions,
            'number_results': number_results,
            'time': round(end-start, 4)
        }

        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write(template.render('templates/index.html', template_values))

