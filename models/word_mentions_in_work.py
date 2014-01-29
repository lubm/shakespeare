from google.appengine.ext import ndb

class WordMentionsInWork(ndb.Model):
    """Models the occurrences of one word inside a work. It has a Word object
       key as its parent."""
    title = ndb.StringProperty()
    mentions = ndb.TextProperty(repeated=True)

    # TODO(luciana): Call super
    #def __init__(self):
    #    """Initializes the list of mentions to empty"""
    #    self.mentions = []
