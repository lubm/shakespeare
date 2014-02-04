"""Test the handler that clears the datastore.

   Follow these steps to run this module:
   nosetests --with-gae --without-sandbox tests/clear_datastore_test.py
   Known GAE issue: https://code.google.com/p/nose-gae/issues/detail?id=60
"""

import unittest
import webtest
import webapp2

from google.appengine.ext import testbed

from models.word import Word
from models.word_mentions_in_work import WordMentionsInWork
from controllers.admin_page import FileMetadata
from controllers.admin_page import ClearDatastoreHandler

class ClearDatastoreTest(unittest.TestCase):
    """Unit test for the action of clearing the datastore."""

    def _set_up_test_datastore(self):
        """Initializes the testbed to allow the creation of a datastore stub."""
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()

    def _insert_into_datastore(self):
        """Insert test objects into the datastore."""
        self.objects = []

        self.objects.append(Word(id='borrower', name='borrower'))
        work = WordMentionsInWork(parent=self.objects[0].key, id='hamlet',
            title='hamlet')
        work.mentions = ['Neither a borrower nor a lender be']
        self.objects.append(work)

        self.objects.append(Word(id='neither', name='neither'))
        work = WordMentionsInWork(parent=self.objects[2].key, id='hamlet',
            title='hamlet')
        work.mentions = ['Neither a borrower nor a lender be']
        self.objects.append(work)

        self.objects.append(FileMetadata(filename='dummy'))
        self.objects.append(FileMetadata(filename='dummy2'))

        self.keys = []
        for obj in self.objects:
            self.keys.append(obj.put())

    def _set_up_test_application(self):
        """Sets up the environment for calling the handler."""
        app = webapp2.WSGIApplication([('/', ClearDatastoreHandler)])
        self.testapp = webtest.TestApp(app)

    def setUp(self):
        """Sets up the datastore and application environment for the test and
           inserts dummy objects into the database.
        """
        self._set_up_test_datastore()
        self._insert_into_datastore()
        self._set_up_test_application()

    def tearDown(self):
        """Deactivates the testbed.
        This restores the original stubs so that tests do not interfere with
        each other.
        """

        self.testbed.deactivate()

    def test_clear_datastore(self):
        """Tests if the database is being cleared and considers non-empty lists
           of instances for all the models used by the application.
        """

        self.assertNotEquals(Word.query().fetch(), [])
        self.assertNotEquals(WordMentionsInWork.query().fetch(), [])
        self.assertNotEquals(list(FileMetadata.all().run()), [])

        self.testapp.get('/')

        self.assertEquals(Word.query().fetch(), [])
        self.assertEquals(WordMentionsInWork.query().fetch(), [])
        self.assertEquals(list(FileMetadata.all().run()), [])

if __name__ == '__main__':
    unittest.main()
