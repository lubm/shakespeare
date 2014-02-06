import unittest

from google.appengine.ext import ndb
from google.appengine.ext import testbed

from models.word import Word
from models.work import Work
from models.character import Character

'''Run this tests like this:
nosetests --with-gae --without-sandbox tests/datastore_test.py
Known GAE issue: https://code.google.com/p/nose-gae/issues/detail?id=60'''

class DatastoreTest(unittest.TestCase):
    def setUp(self):
        ''' Creates an instance of Testbed class and initializes it with the 
        datastore stub.

        Also creates the entities and stores them in the database.'''
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()

        self.word = Word(id="death", name="death", count=2)
        self.work = Work(
            parent=self.word.key, id="Hamlet", title="Hamlet")
        self.character = Character(
            parent=self.work.key, id="Claudius", name="Claudius")

        self.character.mentions = [
            'Though yet of Hamlet our dear brother\'s death']

        self.word_key = self.word.put()
        self.work_key = self.work.put()
        self.character_key = self.character.put()

    def tearDown(self):
        '''Deactivate the testbed. 
        This restores the original stubs so that tests do not interfere with 
        each other.'''

        self.word_key.delete()
        self.work_key.delete()
        self.character_key.delete()

        self.testbed.deactivate()

    def test_insert_entities(self):
        '''Ensures that the entities are saved in the database.

        If we can retrieved they are correctly stored'''
        retrieved_word = self.word_key.get()
        self.assertEqual(2, retrieved_word.count)
        self.assertEqual(2, retrieved_word.count)

        retrieved_work = self.work_key.get()
        self.assertEqual('Hamlet', retrieved_work.title)

        retrieved_character = self.character_key.get()
        self.assertEqual('Claudius', retrieved_character.name)
        self.assertEqual(['Though yet of Hamlet our dear brother\'s death'], 
            retrieved_character.mentions)

    def test_searching_a_non_existing_word(self):
        retrieved_word = Word.get_by_id("sdfgfdgdgf")   
        self.assertEqual(retrieved_word, None)   

    def test_filter_entities_using_query_works(self):
        retrieved_word = Word.get_by_id("death")  
        self.assertEqual('death', retrieved_word.name)
        self.assertEqual(2, retrieved_word.count)

        retrieved_works = Work.query(ancestor=self.word.key).fetch()
        self.assertEqual(len(retrieved_works), 1)
        work = retrieved_works[0]

        retrieved_character = Character.query(ancestor=work.key).fetch()
        self.assertEqual(len(retrieved_character), 1)
        char = retrieved_character[0]
        self.assertEqual(["Though yet of Hamlet our dear brother's death"], 
            char.mentions)


if __name__ == '__main__':
    unittest.main()



