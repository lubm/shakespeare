'''Module for the model of a word.'''
from google.appengine.ext import ndb

class Word(ndb.Model):
    '''Models a word. The relation to mentions is
       represented by MentionsInWork objects, which has the key of a Word object
       as parent.

    Attributes:
        name: the name of the word (or the word itself)
        count: the amount of times the word appears in all the works.
    '''
    name = ndb.StringProperty()
    count = ndb.IntegerProperty()
