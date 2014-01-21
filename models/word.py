from google.appengine.ext import ndb

from models.mention import Mention
from resources.constants import ShakespeareConstants

class Word(ndb.Model):
  """Models a word containing its name and a list of works and lines in which occurs."""
  name = ndb.StringProperty()
  mentions = ndb.StructuredProperty(Mention, repeated=True)

  @classmethod
  def query_repo(cls, ancestor_key):
    return cls.query(ancestor=ancestor_key)

  @classmethod
  def get_from_shakespeare_index(cls, word_id):
    return cls.get_by_id(word_id, parent=ndb.Key(ShakespeareConstants.root_type, ShakespeareConstants.root_key))

  def group_lines_by_work(self):
    work_lines = {}
    for mention in self.mentions:
        if mention.work not in work_lines:
            work_lines[mention.work] = []
        work_lines[mention.work].append(mention.line)
    return work_lines
