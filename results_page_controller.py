"""Module for handling the search results page requests"""

import cgi
import re
import webapp2
import time

from google.appengine.ext.webapp import template

from models.word import Word
from auxiliary.html_formatter import HTMLFormatter
from auxiliary.regex_formatter import RegexFormatter

class ResultsPageController(webapp2.RequestHandler):
    """Class for rendering search results"""

    def get(self):
        """Renders the results of a search"""
        searched_value = self.request.get('searched_word')
        value = searched_value.lower() if searched_value else ''

        work_lines = {}
        if value:
            start = time.time()
            word = Word.get_from_shakespeare_index(cgi.escape(value))
            end = time.time()
            if word:
                word_regex = RegexFormatter.get_any_case_word_regex(word.name)
                work_lines = word.group_lines_by_work()
                for work in work_lines:
                    work_lines[work] = map(
                            lambda line: HTMLFormatter.apply_tag_to_pattern(word_regex, 'b', line),
                            work_lines[work])

        template_values = {
            'searched_word': value,
            'work_mentions': work_lines,
            'number_results': len(work_lines.values()) if work_lines else 0,
            'time': round(end - start, 4)
        }

        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write(template.render('templates/index.html', template_values))

