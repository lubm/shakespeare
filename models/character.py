from google.appengine.ext import ndb

class Character(ndb.Model):
    name = ndb.StringProperty()
    mentions = ndb.StringProperty(repeated=True)

    def __init__(self, *args, **kwargs):
        super(Character, self).__init__(*args, **kwargs)
        self.mentions = []
