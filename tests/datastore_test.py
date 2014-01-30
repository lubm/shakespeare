import unittest

from google.appengine.ext import ndb
from google.appengine.ext import testbed

from models.word import Word
from models.word_mentions_in_work import WordMentionsInWork

"""
Run this tests like this:
nosetests --with-gae --without-sandbox tests/datastore_test.py
Known GAE issue: https://code.google.com/p/nose-gae/issues/detail?id=60
"""

class DatastoreTest(unittest.TestCase):
    def setUp(self):
        """ Creates an instance of Testbed class and initializes it with the 
        datastore stub.

        Also creates the entities and stores them in the database."""
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()

        self.word = Word(id="borrower", name="borrower")
        self.work = WordMentionsInWork(parent=self.word.key, id="hamlet", title="hamlet")
        self.work.mentions = ['Neither a borrower nor a lender be']

        self.word_key = self.word.put()
        self.work_key = self.work.put()

    def tearDown(self):
        """Deactivate the testbed. 
        This restores the original stubs so that tests do not interfere with 
        each other."""

        self.word_key.delete()
        self.work_key.delete()

        self.testbed.deactivate()

    def test_insert_entities(self):
        """Ensures that the entities are saved in the database.

        If we can retrieved they are correctly stored"""
        retrieved_word = self.word_key.get()
        self.assertEqual(self.word.name, retrieved_word.name)

        retrieved_work = self.work_key.get()
        self.assertEqual(self.work.title, retrieved_work.title)
        self.assertEqual(self.work.mentions, retrieved_work.mentions)

    def test_filter_entities_using_query_works(self):
        retrieved_word = Word.get_by_id("borrower")  
        self.assertEqual(self.word.name, retrieved_word.name)

        query_works = WordMentionsInWork.query(ancestor=self.word.key)
        retrieved_works = query_works.fetch()
        self.assertEqual(len(retrieved_works), 1)
        self.assertEqual(retrieved_works[0].mentions, 
            ['Neither a borrower nor a lender be'])


if __name__ == '__main__':
    unittest.main()



