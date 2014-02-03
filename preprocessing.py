""" TODO(izabela): module docstring """

from google.appengine.ext import blobstore
import zipfile
import re
import sys


class Preprocessing(object):
    
    pos_to_character_dicts = []
    ind_to_title = {}
    offset = 0

    def titlecase(self, title):
        return re.sub(r"[A-Za-z]+('[A-Za-z]+)?", lambda mo:
            mo.group(0)[0].upper() + mo.group(0)[1:].lower(), title)

    def get_title(self, my_file):
        line = ''
        while not line.strip():
            line = my_file.readline()
            self.offset += len(line)
        return line.strip()
        

    def parse_file(self, my_file, title):
        """Builds the dict that maps file offset to character.

        Args:


        """
        charac = ''
        pos_to_char = {}
        line = my_file.readline()
        reg = re.compile('([^\s]+)\t.*$')
        # Find title repeated
        print title
        while title not in line:
            self.offset += len(line)
            line = my_file.readline()
        while line:
            if line.strip():
                # if line has character
                match = reg.match(line)
                if match:
                    charac = match.group(1)
                pos_to_char[self.offset] = charac
            self.offset += len(line)
            line = my_file.readline()
        self.pos_to_character_dicts.append(pos_to_char)


    def run(self, blob_key):
        """Open a zipfile and preprocess each of its text files.

        Args:
        
        """
        blob_reader = blobstore.BlobReader(blob_key)
        with zipfile.ZipFile(blob_reader) as zip_files:
            for count, name in enumerate(zip_files.namelist()):
                with zip_files.open(name, 'r') as my_file:
                    title = self.get_title(my_file)
                    self.ind_to_title[count] = self.titlecase(title)
                    self.parse_file(my_file, title)

