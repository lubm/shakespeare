"""Character model for the datastore."""
from google.appengine.ext import ndb

from models.line import Line

class Character(ndb.Model):
    """Model a Character of a Work. The parent of this object is a Work.

    It contains a list of mentions of a word in an specific work, said by this
    character.

    Attributes:
        name: Name of the character.
        mentions: List of the keys for lines said by this character.
    """
    name = ndb.StringProperty()
    mentions = ndb.KeyProperty(kind=Line, repeated=True)

    def __init__(self, *args, **kwargs):
        """Initialize the character with an empty list of mentions."""
        super(Character, self).__init__(*args, **kwargs)
        self.mentions = []

    def get_string_mentions(self):
        """Get all mentions as strings"""
        return [mention_key.get().line for mention_key in self.mentions]
