'''Module for the model of a word.'''
from google.appengine.ext import ndb

from models.work import Work

class Word(ndb.Model):
    '''Models a word. The relation to mentions is
       represented by MentionsInWork objects, which has the key of a Word object
       as parent.

    Attributes:
        name: the name of the word (or the word itself)
        count: the amount of times the word appears in all the works.
    '''
    name = ndb.StringProperty()
    works = ndb.KeyProperty(kind=Work, repeated=True)
    count = ndb.IntegerProperty()
    
    def __init__(self, *args, **kwargs):
        """Initialize the word's works with an empty list."""
        super(Word, self).__init__(*args, **kwargs)
        self.works = []

