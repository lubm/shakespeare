"""Module for handling the search results page requests"""

import cgi
import webapp2
import time
from webapp2_extras import json

from google.appengine.ext import ndb

from models.character import Character
from models.word import Word
from models.work import Work
from resources.constants import Constants
import auxiliary.spelling_corrector as spelling_corrector
import auxiliary.formatter as formatter


_PAGE_LIM = 10

def _bold_mentions(word_name, mentions):
    """Turns into bold certain word in textual mentions.

    Args:
        word_name: the word string representation.
        mentions: the list of line strings in which the word appear.

    Returns:
        The list of mentions with the word names within bold HTML tags.
    """

    word_regex = formatter.get_any_case_word_regex(word_name)
    return [
        formatter.apply_tag_to_pattern(word_regex, Constants.BOLD_TAG,
            line) for line in mentions]


def _get_word_mentions(word_name):
    """Get all the mentions of a certain word string representation accessed
       first by work and then by character.

    Args:
        word_name: the string representation of the word.

    Returns:
        A dictionary of dictionaries, being the first key the work title and the
        second, the character name.
    """
    all_mentions = {}
    word = Word.get_by_id(word_name)
    if not word:
        return {}, 0
    works = ndb.get_multi(word.works)
    work_lim = _PAGE_LIM / len(works) if word.count > _PAGE_LIM else None
    for work in works:
        work_chars = ndb.get_multi(work.characters)
        all_mentions[work.title] = {}
        number_of_results = 0
        for char in work_chars:
            available_amount = work_lim - number_of_results if work_lim else \
                None
            if work_lim and available_amount <= 0:
                break
            mentions = char.get_string_mentions(available_amount=
                available_amount)
            number_of_results += len(mentions)
            bold_mentions = _bold_mentions(word.name, mentions)
            all_mentions[work.title][char.name] = bold_mentions
    return all_mentions, word.count, work_lim


def _get_word_mentions_in_work(word_name, work_title):
    """Get all mentions of a word that appear in a certain work.

    Args:
        word_name: the string of the word being searched (lowercase).
        work_title: the title of the work (titlecase).

    Returns:
        A dictionary first indexed by work and second by character. The work is
        inserted to comply with the data pattern.
    """

    word = Word.get_by_id(word_name)
    if not word:
        return {}, 0
    work = Work.get_by_id(word_name + work_title)
    if not work:
        return {}, 0
    chars = ndb.get_multi(work.characters)
    mentions_dict = {work_title: {}}
    for char in chars:
        mentions = char.get_string_mentions()
        bold_mentions = _bold_mentions(word_name, mentions)
        mentions_dict[work_title][char.name] = bold_mentions
    return mentions_dict, work.count


def _get_word_mentions_by_char(word_name, work_title, char_name):
    """Get the words that a said by a character of a certain work

    Args:
        word_name: the string of the word being searched (lowercase).
        work_title: the title of the work in which the character appears
            (titlecase).
        char_name: the name of the character (titlecase).

    Returns:
        A dictionary indexed by the work and the characters. This redundant data
        is created in order to comply with the data pattern.
    """

    word = Word.get_by_id(word_name)
    if not word:
        return {}, 0
    work = Work.get_by_id(word_name + work_title)
    if not work:
        return {}, 0
    char = Character.get_by_id(word_name + work_title + char_name)
    if not char:
        return {}, 0
    mentions = char.get_string_mentions()
    bold_mentions = _bold_mentions(word_name, mentions)
    mentions_dict = {work_title: {char_name: bold_mentions}}
    return mentions_dict, char.count


def _get_work_characters(word_name, work_title):
    """Retrieves all the characters that mentions a word in a given work.

    Args:
        word_name: the string of the word which the characters mention
            (lowercase).
        work_title: the title of the work of interest (titlecase).

    Returns:
        A list with the names of the characters.
    """

    word = Word.get_by_id(word_name)
    if not word:
        return []
    work = Work.get_by_id(word_name + work_title)
    if not work:
        return []
    chars = ndb.get_multi(work.characters)
    char_names = [char.name for char in chars]
    return char_names


def _get_word_works(word_name):
    """Retrieves all the works in which a word occurs.

    Args:
        word_name: the word (lowercase).

    Returns:
        A list with the titles of the works.
    """

    word = Word.get_by_id(word_name)
    if not word:
        return []
    works = ndb.get_multi(word.works)
    work_titles = [work.title for work in works] 
    return work_titles


class ResultsPageController(webapp2.RequestHandler):
    """Class for rendering search results"""

    def get(self):
        """Renders the results of a search"""
        searched_value = self.request.get('searched_word')
        value = searched_value.lower() if searched_value else ''

        works = _get_word_works(value)

        template_values = {
            'searched_word': value,
            'works': works,
        }

        self.response.headers['Content-Type'] = 'text/html'
        template = Constants.JINJA_ENVIRONMENT.get_template('results.html')
        self.response.write(template.render(template_values))


class TreemapHandler(webapp2.RequestHandler):
    """Class for retrieving data for the visualization"""

    def get(self):
        """Retrieves formatted information to the treemap visualization. It
           expects a list of elements, and each element is a list of the
           following type:

           [name, parent's name, value, color value]

           In which name and parent's name are strings, value is an integer
           proportional to the size of the resulting rectangle on the treemap
           and color value is the value to be used as color acording to the
           color range.

           It is called the function get_word_mentions to obtain a
           dictionary that maps from work and character to mentions.
        """
        searched_value = cgi.escape(self.request.get('searched_word').lower())

        if not searched_value:
            return
        
        word = Word.get_by_id(searched_value)
        if not word:
            return

        treemap_data = [['Location', 'Parent', 'Word Occurrences'],
            ['Shakespeare\'s Corpus', None, word.count]]

        works = ndb.get_multi(word.works)
        for work in works:
            treemap_data.append([work.title, 'Shakespeare\'s Corpus', 
                work.count]) 
            chars = ndb.get_multi(work.characters)
            for char in chars:
                treemap_data.append([{'v': work.title + '+' + char.name, 'f':
                    char.name}, work.title, char.count])

        self.response.headers['Content-Type'] = 'text/json'
        self.response.out.write(json.encode({"array": treemap_data}))


class CharactersHandler(webapp2.RequestHandler):
    """Class for retrieving characters associated to a given work."""

    def get(self):
        """Returns the characters of a work."""
        word_value = cgi.escape(self.request.get('searched_word').lower())
        work_value = self.request.get('work_filter')
        chars = _get_work_characters(word_value, work_value)

        self.response.headers['Content-Type'] = 'text/json'
        self.response.out.write(json.encode({'chars': chars}))


class WorksHandler(webapp2.RequestHandler):
    """Class for retrieving works associated to a given word."""

    def get(self):
        """Returns the works that refers to a word."""
        word_value = cgi.escape(self.request.get('searched_word').lower())
        works = _get_word_works(word_value)

        self.response.headers['Content-Type'] = 'text/json'
        self.response.out.write(json.encode({'works': works}))


class SearchHandler(webapp2.RequestHandler):
    """Class for receiving request of filtering results by work and
       character."""

    def get(self):
        """Returns the mentions related to a specific work and character"""
        word_value = cgi.escape(self.request.get('searched_word').lower())
        work_value = self.request.get('work_filter')
        char_value = self.request.get('char_filter')
        work_limit = None

        start = time.time()
        if work_value == 'Any':
            mentions, count, work_limit = _get_word_mentions(word_value)
        else:
            if char_value == 'Any':
                mentions, count = _get_word_mentions_in_work(word_value, 
                    work_value)
            else:
                mentions, count = _get_word_mentions_by_char(word_value, 
                    work_value, char_value)
        end = time.time()

        result = {
            'mentions': mentions,
            'number_results': count,
            'work_limit': str(work_limit),
            'time': round(end - start, 4),
            'did_you_mean': spelling_corrector.get_suggestion(word_value)
        }
        
        self.response.headers['Content-Type'] = 'text/json'
        self.response.out.write(json.encode(result))
