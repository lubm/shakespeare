"""Character model for the datastore."""
from google.appengine.ext import ndb

from models.line import Line

class Character(ndb.Model):
    """Model a Character of a Work. The parent of this object is a Work.

    It contains a list of mentions of a word in an specific work, said by this
    character.

    Attributes:
        name: Name of the character.
        mentions: List of the keys for lines (that contains an specific word)
            said by this character. 
            This list is actually a set: if the word is repeated more than one
            time in the line, the character would not have the line repeated. 
        count: The number of times a character says an specific word inside a
            book.
    """
    name = ndb.StringProperty()
    mentions = ndb.KeyProperty(kind=Line, repeated=True)
    count = ndb.IntegerProperty()

    def __init__(self, *args, **kwargs):
        """Initialize the character with an empty list of mentions."""
        super(Character, self).__init__(*args, **kwargs)
        self.mentions = []

    def get_string_mentions(self, available_amount=None):
        """Get all mentions as strings"""
        if available_amount:
            return [mention.line for mention in
                    ndb.get_multi(self.mentions[:available_amount])]
        return [mention.line for mention in ndb.get_multi(self.mentions)]
