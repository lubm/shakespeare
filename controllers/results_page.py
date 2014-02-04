"""Module for handling the search results page requests"""

import cgi
import webapp2
import time

from google.appengine.ext.webapp import template

from auxiliary.html_formatter import HTMLFormatter
from auxiliary.regex_formatter import RegexFormatter
from models.character import Character
from models.word import Word
from models.work import Work
from resources.constants import Constants

def bold_mentions(word_name, mentions):
    """Turns into bold certain word in textual mentions.

    Args:
        word_name: the word string representation.
        mentions: the list of line strings in which the word appear.

    Returns:
        The list of mentions with the word names within bold HTML tags.
    """
    
    word_regex = RegexFormatter.get_any_case_word_regex(word_name)
    return [
        HTMLFormatter.apply_tag_to_pattern(word_regex, Constants.BOLD_TAG,
            line) for line in mentions]


def count_dict_values(dictionary):
    """Counts the amount of values regarding all keys in a dictionary.

    Args:
        dictionary: a dictionary to count the values.

    Returns:
        An integer with the amount of values.
    """
    count = 0
    for key in dictionary:
        count += len(dictionary[key])
    return count


def get_work_mentions_of_word_name(word_name):
    """Get all the mentions of a certain word string representation grouped by
       work.

    Args:
        word_name: the string representation of the word.

    Returns:
        A dictionary with work titles as keys and lines with mentions of the
        word as values.
    """
    work_mentions = {}
    word = Word.get_by_id(word_name)
    if word:
        works = Work.query(ancestor=word.key)
        for work in works:
            work_chars = Character.query(ancestor=work.key)
            mentions = []
            for char in work_chars:
                mentions += char.mentions
            work_mentions[work.title] = bold_mentions(word.name, mentions)
    return work_mentions


class ResultsPageController(webapp2.RequestHandler):
    """Class for rendering search results"""

    def get(self):
        """Renders the results of a search"""
        searched_value = self.request.get('searched_word')
        value = searched_value.lower() if searched_value else ''

        if value:
            start = time.time()
            work_mentions = get_work_mentions_of_word_name(cgi.escape(value))
            end = time.time()

        template_values = {
            'searched_word': value,
            'work_mentions': work_mentions,
            'number_results': count_dict_values(work_mentions),
            'time': round(end - start, 4)
        }

        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write(template.render('templates/results.html',
            template_values))
