"""Module for the model of a word mention"""

from google.appengine.ext import ndb

class Mention(ndb.Model):
    """Models a mention of a word in a line of a Shakespear's work."""
    work = ndb.StringProperty()
    line = ndb.StringProperty()
