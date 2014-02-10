"""Test the handler that clears the datastore.

   Follow these steps to run this module:
   nosetests --with-gae --without-sandbox tests/clear_datastore_test.py
   Known GAE issue: https://code.google.com/p/nose-gae/issues/detail?id=60
"""

import unittest
import webtest
import webapp2

from google.appengine.ext import testbed

from models.character import Character
from models.word import Word
from models.work import Work
from models.line import Line
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

        word = Word(id='borrower', name='borrower', count=1)
        work = Work(parent=word.key, id='hamlet', title='hamlet', count=1)
        char_1 = Character(parent=work.key, id='hamlet', name='hamlet', count=1)
        char_2 = Character(parent=work.key, id='guard', name='guard', count=1)
        line_1 = Line(line='Neither a borrower nor a lender be').put()
        line_2 = Line(line='To be or not to be.').put()

        char_1.mentions = [line_1, line_2]
        line_3 = Line(line='Ok, boss!').put()
        char_2.mentions = [line_3]

        self.objects += [word, work, char_1, char_2]

        word = Word(id='neither', name='neither', count=1)
        work = Work(parent=word.key, id='hamlet', title='hamlet', count=1)
        char = Character(parent=work.key, id='hamlet', name='hamlet', count=1)
        line = Line(line='Neither a borrower nor a lender be').put()
        char.mentions = [line]
        self.objects += [word, work, char]

        self.objects += [FileMetadata(filename='dummy'), 
            FileMetadata(filename='dummy2')]

        for obj in self.objects:
            obj.put()

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
        self.assertNotEquals(Work.query().fetch(), [])
        self.assertNotEquals(Character.query().fetch(), [])
        self.assertNotEquals(list(FileMetadata.all().run()), [])

        self.testapp.get('/')

        self.assertEquals(Word.query().fetch(), [])
        self.assertEquals(Work.query().fetch(), [])
        self.assertEquals(Character.query().fetch(), [])
        self.assertEquals(list(FileMetadata.all().run()), [])

if __name__ == '__main__':
    unittest.main()
