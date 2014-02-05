import unittest

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

    def test_correct_a_word(self):
        self.assertEqual(self.spelling_corrector.edits1('lave'), [])
