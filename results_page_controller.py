"""Module for handling the search results page requests"""

import cgi
import webapp2
import time
import logging

from google.appengine.ext.webapp import template

from models.word import Word
from models.work import Work
from auxiliary.html_formatter import HTMLFormatter
from auxiliary.regex_formatter import RegexFormatter


class ResultsPageController(webapp2.RequestHandler):
    """Class for rendering search results"""

    def get(self):
        """Renders the results of a search"""
        searched_value = self.request.get('searched_word')
        value = searched_value.lower() if searched_value else ''

        # TODO(luciana): Refactor into shorter functions
        work_lines = {}
        if value:
            start = time.time()
            word = Word.get_by_id(cgi.escape(value))
            end = time.time()
            if word:
                word_regex = RegexFormatter.get_any_case_word_regex(word.name)
                works = Work.query_works(word.key)
                for work in works:
                    # TODO(luciana): Highlight on javascript
                    work_lines[work.title] = map(
                        lambda line: HTMLFormatter.apply_tag_to_pattern(
                            word_regex, 'b', line),
                        work.mentions)
                    logging.info('---------------Mentions in work ' + str(work.mentions))

        template_values = {
            'searched_word': value,
            'work_mentions': work_lines,
            # TODO(luciana): Create a separate function, change to list
            # comprehension
            'number_results': reduce(lambda x, y: x + len(y),
                work_lines.values(), 0),
            'time': round(end - start, 4)
        }

        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write(template.render('templates/index.html',
            template_values))
