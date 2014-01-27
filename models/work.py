from google.appengine.ext import ndb

from models.mention import Mention

class MentionsInWork(ndb.Model):
    """Models the occurrences of one word inside a work"""
    title = ndb.StringProperty()
    mentions = ndb.StringProperty(repeated=True)
