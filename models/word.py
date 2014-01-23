"""Module for the model of a word"""
from google.appengine.ext import ndb

from models.mention import Mention
from resources.constants import ShakespeareConstants

class Word(ndb.Model):
    """Models a word containing its name and a list of works where it occurs"""
    name = ndb.StringProperty()
    mentions = ndb.StructuredProperty(Mention, repeated=True)

    @classmethod
    def query_repo(cls, ancestor_key):
        """Get all the words inside the repo"""
        return cls.query(ancestor=ancestor_key)

    # TODO: Delete after removing the parent.
    @classmethod
    def get_from_shakespeare_index(cls, word_id):
        """Retrieves a word using the index"""
        return cls.get_by_id(word_id, parent=ndb.Key(
            ShakespeareConstants.root_type, ShakespeareConstants.root_key))

    # TODO: Delete after we refactor the datastore architecture.
    def group_lines_by_work(self):
        """Changes the mentions structure to retrieve lines grouped by works"""
        work_lines = {}
        for mention in self.mentions:
            if mention.work not in work_lines:
                work_lines[mention.work] = []
            work_lines[mention.work].append(mention.line)
        return work_lines
