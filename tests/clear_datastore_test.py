import unittest
import webtest
import webapp2

from google.appengine.ext import ndb
from google.appengine.ext import testbed

from models.word import Word
from models.word_mentions_in_work import WordMentionsInWork
from controllers.admin_page import FileMetadata

from controllers.admin_page import ClearDatastoreHandler

"""
Run this tests like this:
nosetests --with-gae --without-sandbox tests/datastore_test.py
Known GAE issue: https://code.google.com/p/nose-gae/issues/detail?id=60
"""

class DatastoreTest(unittest.TestCase):
    def setUp(self):
        """ Creates an instance of Testbed class and initializes it with the 
        datastore stub.

        Also creates the entities and stores them in the database. All kinds of
        entities inserted in the datastore during the life span of the
        application are included.
        """
        
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()

        self.objects = []

        self.objects.append(Word(id="borrower", name="borrower"))
        work = WordMentionsInWork(parent=self.objects[0].key, id="hamlet", 
            title="hamlet")
        work.mentions = ['Neither a borrower nor a lender be']
        self.objects.append(work)

        self.objects.append(Word(id="neither", name="neither"))
        work = WordMentionsInWork(parent=self.objects[2].key, id="hamlet", 
            title="hamlet")
        work.mentions = ['Neither a borrower nor a lender be']
        self.objects.append(work)

        self.objects.append(FileMetadata(filename="dummy"))
        self.objects.append(FileMetadata(filename="dummy2"))

        self.keys = []
        for obj in self.objects:
            self.keys.append(obj.put())

        """ Setting up the environment of the handler """
        app = webapp2.WSGIApplication([('/', ClearDatastoreHandler)])
        self.testapp = webtest.TestApp(app)

    def tearDown(self):
        """Deactivate the testbed. 
        This restores the original stubs so that tests do not interfere with 
        each other."""

        #for key in self.keys:
            #key.delete()

        self.testbed.deactivate()

    def test_clear_datastore(self):
        """Clears the whole database, i.e., all the datastore entities"""
        
        response = self.tesapp.get('/')
        self.assertEqual(Word.query().fetch(), [])
        self.assertEqual(WordMentionsInWork.query().fetch(), [])
        self.assertEqual(FileMetadata.query().fetch(), [])


if __name__ == '__main__':
    unittest.main()
