from google.appengine.ext import ndb

from models.character import Character

class Work(ndb.Model):
    """Models the occurrences of one word inside a work. It has a Word object
       key as its parent.

    Attributes:
    	title: Title of the book. We use the first capitalized string in the
    		begining of the book. But we stored titlecased (Hamlet instead of
    		HAMLET).
		count: The number of times a character says this word inside a book.
    	"""
    title = ndb.StringProperty()
    characters = ndb.KeyProperty(kind=Character, repeated=True)
    count = ndb.IntegerProperty()
    
    def __init__(self, *args, **kwargs):
        """Initialize the work's characters with an empty list."""
        super(Work, self).__init__(*args, **kwargs)
        self.characters = []
