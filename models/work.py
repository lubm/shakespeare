from google.appengine.ext import ndb

class Work(ndb.Model):
    """Models the occurrences of one word inside a work. It has a Word object
       key as its parent."""
    title = ndb.StringProperty()
