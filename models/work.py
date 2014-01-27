from google.appengine.ext import ndb

class Work(ndb.Model):
    """Models the occurrences of one word inside a work"""
    title = ndb.StringProperty()
    mentions = ndb.TextProperty(repeated=True)

    # TODO(luciana): Call super
    #def __init__(self):
    #    """Initializes the list of mentions to empty"""
    #    self.mentions = []

    @classmethod
    def query_works(cls, ancestor_key):
        """Get all the words inside the repo"""
        return cls.query(ancestor=ancestor_key)
