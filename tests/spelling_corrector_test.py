import unittest
import random

from google.appengine.ext import ndb
from google.appengine.ext import testbed

from models.word import Word
import auxiliary.spelling_corrector as spelling_corrector

"""
Run this tests like this:
nosetests --with-gae --without-sandbox tests/datastore_test.py
Known GAE issue: https://code.google.com/p/nose-gae/issues/detail?id=60
"""

class SpellingCorrectorTest(unittest.TestCase):
    def setUp(self):
        """ Creates an instance of Testbed class and initializes it with the 
        datastore stub.

        Also creates the words and stores them in the database."""
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()

        self.borrower = Word(id="borrower", name="borrower", count=2)
        self.love = Word(id="love", name="love", count=12)

        self.borrower_key = self.borrower.put()
        self.love_key = self.love.put()

        self.spelling_corrector_object = spelling_corrector.SpellingCorrector()

    def tearDown(self):
        """Deactivate the testbed. 
        This restores the original stubs so that tests do not interfere with 
        each other."""

        self.borrower_key.delete()
        self.love_key.delete()

        self.testbed.deactivate()

    def test_generate_splits_of_a_word(self):
        self.assertEqual(spelling_corrector._splits('love'), 
            [('', 'love'), ('l', 'ove'), ('lo', 've'), ('lov', 'e'), 
            ('love', '')])

    def test_generate_deletes_of_a_list_of_splited_words(self):
        self.assertEqual(spelling_corrector._deletes(
            [('lo', 've'), ('l', 'ove')]), 
            ['loe', 'lve'])

    def test_generate_transposes_of_a_list_of_splited_words(self):
        self.assertEqual(spelling_corrector._transposes(
            [('lo', 've'), ('l', 'ove')]), 
            ['loev', 'lvoe'])

    def test_generate_replaces_of_a_list_of_splited_words(self):
        replaces = []
        for letter in 'abcdefghijklmnopqrstuvwxyz':
            replaces.append('lo' + letter + 'e')
        for letter in 'abcdefghijklmnopqrstuvwxyz':
            replaces.append('l' + letter + 've')
        self.assertEqual(spelling_corrector._replaces(
            [('lo', 've'), ('l', 'ove')]), replaces)

    def test_generate_inserts_of_a_list_of_splited_words(self):
        inserts = []
        for letter in 'abcdefghijklmnopqrstuvwxyz':
            inserts.append('lo' + letter + 've')
        for letter in 'abcdefghijklmnopqrstuvwxyz':
            inserts.append('l' + letter + 'ove')
        self.assertEqual(spelling_corrector._inserts(
            [('lo', 've'), ('l', 'ove')]), inserts)

    def test_words_edit_distance_one_should_contain_all_the_types(self):
        option1 = random.choice(spelling_corrector._deletes([('lo', 've'), ('l', 'ove')]))

        option2 = random.choice(spelling_corrector._replaces([('lo', 've'), ('l', 'ove')]))

        option3 = random.choice(spelling_corrector._transposes([('lo', 've'), ('l', 'ove')]))

        option4 = random.choice(spelling_corrector._inserts([('lo', 've'), ('l', 'ove')]))

        self.assertTrue(option1 in 
            spelling_corrector._words_edit_distance_one('love'))

        self.assertTrue(option2 in 
            spelling_corrector._words_edit_distance_one('love'))

        self.assertTrue(option3 in 
            spelling_corrector._words_edit_distance_one('love'))

        self.assertTrue(option4 in 
            spelling_corrector._words_edit_distance_one('love'))

    def test_get_candidates(self):
        self.assertEqual(spelling_corrector._get_candidates(['lve']), [])
        retrieved_result = spelling_corrector._get_candidates(['love', 'borrower'])
        self.assertEqual(len(retrieved_result), 2)
        self.assertEqual(retrieved_result[0].name, 'love')
        self.assertEqual(retrieved_result[1].name, 'borrower')

    def test_correct_if_there_is_only_one_candidate(self):
        self.assertEqual(spelling_corrector.get_suggestion('lve'), 'love')
        self.assertEqual(spelling_corrector.get_suggestion('borruwer'), 'borrower')

    def test_correct_if_there_is_multiple_candidates(self):
        Word(id="lave", name="lave", count=1).put()
        self.assertEqual(spelling_corrector.get_suggestion('lve'), 'love')
        Word(id="lie", name="lie", count=100).put()
        self.assertEqual(spelling_corrector.get_suggestion('lve'), 'lie')

    def test_dont_show_suggestion_is_there_are_no_suggestions(self):
        self.assertEqual(spelling_corrector.get_suggestion('jdsjhdgfjdkahgd'), None)

    def test_if_the_word_is_found_no_show_suggestions(self):
        self.assertEqual(spelling_corrector.get_suggestion('love'), None)

