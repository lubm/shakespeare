"""Module for the model of a word"""
from google.appengine.ext import ndb

class Word(ndb.Model):
    """Models a word containing its name and a list of works where it occurs"""
    name = ndb.StringProperty()
