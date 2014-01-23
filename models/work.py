from google.appengine.ext import ndb

from models.mention import Mention

class Work(ndb.Model):
    """Models the occurrences of one word inside a work"""
    name = ndb.StringProperty()
    mentions = ndb.StringProperty(repeated=True)

    @classmethod
    def query_work(cls, ancestor_key):
        return cls.query(ancestor=ancestor_key)
