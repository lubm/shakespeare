from google.appengine.ext import ndb

from models.mention import Mention

class Word(ndb.Model):
  """Models a word containing its name and a list of works and lines in which occurs."""
  name = ndb.StringProperty()
  mentions = ndb.StructuredProperty(Mention, repeated=True)

  @classmethod
  def query_repo(cls, ancestor_key):
    return cls.query(ancestor=ancestor_key)

  @classmethod
  def get_from_index(cls, word_id):
    return cls.get_by_id(word_id, parent=ndb.Key('Index', 'Shakespeare')) #TODO: constants file
