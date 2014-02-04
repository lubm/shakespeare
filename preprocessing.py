""" A module to preprocess Shakespeare's works, gathering metadata."""
#TODO(izabela): treat files that do not follow the pattern

from google.appengine.ext import blobstore
import zipfile
import re


class Preprocessing(object):
    """Preprocess Shakespeare's works to identify titles and characters.

        The preprocessing builds two important data strucutures. The first is a
        map(index, title) that relates the index of a text file (regarding its
        position in the zip file provided) to the title of the work it refers
        to. The second data structure is a list of maps. The i-th map is related
        to the i-th text file. Each map is of the form (offset, character), in
        which offset is the byte-offset of each line of text pronounced by a
        character.

    """

    pos_to_character_dicts = []
    ind_to_title = {}
    offset = 0

    def __init__(self, blob_key):
        """Initialize the preprocessing object and run it.

        Args:
            blob_key: A blob key to a zip file containing one or more text files
        """
        self.blob_key = blob_key
        self.run()

    @staticmethod
    def titlecase(title):
        """Capitalize first letter of each word."""
        return re.sub(r"[A-Za-z]+('[A-Za-z]+)?", lambda mo:
            mo.group(0)[0].upper() + mo.group(0)[1:].lower(), title)

    def get_title(self, my_file):
        """Retrieve first non_empty line of file as title.

        Args:
            my_file: file handler of file to be processed

        Returns:
            title: string
        """
        line = ''
        while not line.strip():
            line = my_file.readline()
            self.offset += len(line)
        return line.strip()

    def parse_file(self, my_file, title):
        """Builds the dict that maps file offset to character.

        Args:
            my_file: file handler of file to be processed
            title: string containing title of work
        """
        charac = ''
        pos_to_char = {}
        line = my_file.readline()
        reg = re.compile(r'([^\s]+)\t.*$')
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

    def run(self):
        """Open a zipfile and preprocess each of its text files."""
        blob_reader = blobstore.BlobReader(self.blob_key)
        with zipfile.ZipFile(blob_reader) as zip_files:
            for count, name in enumerate(zip_files.namelist()):
                with zip_files.open(name, 'r') as my_file:
                    title = self.get_title(my_file)
                    self.ind_to_title[count] = self.titlecase(title)
                    self.parse_file(my_file, title)

