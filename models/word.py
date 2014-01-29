"""Module for the model of a word"""
from google.appengine.ext import ndb

class Word(ndb.Model):
    """Models a word containing its name. The relation to mentions is
       represented by MentionsInWork objects, which has the key of a Word object
       as parent.
    """
    name = ndb.StringProperty()
