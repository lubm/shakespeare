import os
import re
import string

from models.mention import Mention
from models.word import Word

from google.appengine.ext import ndb

root_type = 'Index'
root_key = 'Shakespeare'

class Parser(object):
    """Parse all text files from given directory and creates an index on Datastore"""
    def __init__(self, data_dir):
        self.data_dir = data_dir
        if self.data_dir[-1] != '/':
            self.data_dir += '/'
        self.parent = ndb.Key(root_type, root_key)

    def parse(self):
        for file_name in os.listdir(self.data_dir):
            data_file = open(self.data_dir + file_name, 'r')
            i = 0
            for line in data_file:
                # REMOVE LINE PRINT
                i += 1
                print i
                line = line.strip()
                if line:
                    words = set(map(string.lower, re.sub('[^\w]', ' ', line).split()))
                    for word in words:
                        word_data = Word.get_by_id(word, parent=self.parent)
                        
                        if not word_data:
                            word_data = Word(parent=self.parent, 
                                    id=word, name=word)
                        new_mention = Mention(line=line, work=file_name)
                        if word_data.mentions:
                            word_data.mentions.append(new_mention)
                        else:
                            word_data.mentions = [new_mention]
                        word_data.put()
