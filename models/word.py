from google.appengine.ext import ndb

from models.mention import Mention
from models.work import Work
from resources.constants import ShakespeareConstants

class Word(ndb.Model):
    """Models a word containing its name and a list of works where it occurs"""
    name = ndb.StringProperty()
