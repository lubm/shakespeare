"""Mention model for a line in a work."""
from google.appengine.ext import ndb

class Line(ndb.Model):
    """Model a mention in a work."""

    line = ndb.StringProperty()
