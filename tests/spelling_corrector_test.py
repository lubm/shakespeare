import unittest
import random

from google.appengine.ext import ndb
from google.appengine.ext import testbed

from models.word import Word
from auxiliary.spelling_corrector import SpellingCorrector
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

        self.spelling_corrector = SpellingCorrector()

    def tearDown(self):
        """Deactivate the testbed. 
        This restores the original stubs so that tests do not interfere with 
        each other."""

        self.borrower_key.delete()
        self.love_key.delete()

        self.testbed.deactivate()

    def test_generate_splits_of_a_word(self):
        self.assertEqual(self.spelling_corrector.splits('love'), 
            [('', 'love'), ('l', 'ove'), ('lo', 've'), ('lov', 'e'), 
            ('love', '')])

    def test_generate_deletes_of_a_list_of_splited_words(self):
        self.assertEqual(self.spelling_corrector.deletes(
            [('lo', 've'), ('l', 'ove')]), 
            ['loe', 'lve'])

    def test_generate_transposes_of_a_list_of_splited_words(self):
        self.assertEqual(self.spelling_corrector.transposes(
            [('lo', 've'), ('l', 'ove')]), 
            ['loev', 'lvoe'])

    def test_generate_replaces_of_a_list_of_splited_words(self):
        replaces = []
        for letter in 'abcdefghijklmnopqrstuvwxyz':
            replaces.append('lo' + letter + 'e')
        for letter in 'abcdefghijklmnopqrstuvwxyz':
            replaces.append('l' + letter + 've')
        self.assertEqual(self.spelling_corrector.replaces(
            [('lo', 've'), ('l', 'ove')]), replaces)

    def test_generate_inserts_of_a_list_of_splited_words(self):
        inserts = []
        for letter in 'abcdefghijklmnopqrstuvwxyz':
            inserts.append('lo' + letter + 've')
        for letter in 'abcdefghijklmnopqrstuvwxyz':
            inserts.append('l' + letter + 'ove')
        self.assertEqual(self.spelling_corrector.inserts(
            [('lo', 've'), ('l', 'ove')]), inserts)

    def test_words_edit_distance_one_should_contain_all_the_types(self):
        option1 = random.choice(
            self.spelling_corrector.deletes([('lo', 've'), ('l', 'ove')]))

        option2 = random.choice(
            self.spelling_corrector.replaces([('lo', 've'), ('l', 'ove')]))

        option3 = random.choice(
            self.spelling_corrector.transposes([('lo', 've'), ('l', 'ove')]))

        option4 = random.choice(
            self.spelling_corrector.inserts([('lo', 've'), ('l', 'ove')]))

        self.assertTrue(option1 in 
            self.spelling_corrector.words_edit_distance_one('love'))

        self.assertTrue(option2 in 
            self.spelling_corrector.words_edit_distance_one('love'))

        self.assertTrue(option3 in 
            self.spelling_corrector.words_edit_distance_one('love'))

        self.assertTrue(option4 in 
            self.spelling_corrector.words_edit_distance_one('love'))


    def test_words_edit_distance_two(self):
        Word(id="borwer", name="borwer", count=4).put()
        
        self.assertTrue('borwer' 
            in self.spelling_corrector.words_edit_distance_two('borrower'))
