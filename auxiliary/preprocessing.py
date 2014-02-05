""" A module to preprocess Shakespeare's works, gathering metadata."""
#TODO(izabela): treat files that do not follow the pattern

from google.appengine.ext import blobstore
import zipfile
import re

_preprocessing = None

class FileIndexTooLargeError(Exception):
    """To be raised when a file index that does not exist is requested."""
    def __init__(self, num_files, index_requested):
        self.num_files = num_files
        self.ind_requested = index_requested

    def __repr__(self):
        return '''Preprocessing only identified %d files in zipfile and %d file
            index was requested.''', self.num_files, self.ind_requested

    def __str__(self):
        return repr(self)

class Preprocessing(object):
    """Preprocess Shakespeare's works to identify titles and characters.

        The preprocessing builds two important data strucutures. The first is a
        map(index, title) that relates the index of a text file (regarding its
        position in the zip file provided) to the title of the work it refers
        to. The second data structure is a list of maps. The i-th map is related
        to the i-th text file. Each map is of the form (offset, character), in
        which offset is the byte-offset of each line of text pronounced by a
        character.

        This attributes are global in order to be able to access them from
            inside our mapreduce functions.

        Attributes:
            ind_to_title: Dictionary that relates the index of a text file to
                the title of the work it refers to.
            pos_to_character_dicts: Dictionary that relates the index of a text
                file to the title of the work it refers to.
            offset: Value used to iterate each file.

    """
        pos_to_character_dicts = []
        ind_to_title = {}
        offset = 0

    @staticmethod
    def titlecase(title):
        """Capitalize first letter of each word.

        Args:
            title: The title of the work, found in the first line of each file.
                This title is stripped(doesn't have any trailing spaces or
                front spaces).
                Examples: 'LOVE'S LABOUR'S LOST', 'OTHELLO'.

        Returns:
            This title but with only the first letter of each word capitalized.
        """
        return re.sub(r"[A-Za-z]+('[A-Za-z]+)?", lambda mo:
            mo.group(0)[0].upper() + mo.group(0)[1:].lower(), title)

    @classmethod
    def find_title(cls, my_file):
        """Retrieve first non_empty line of file as title.

        Also, it sets the offset attribute to hold the position of the last
        character in the title line.

        Args:
            my_file: file handler of file to be processed

        Returns:
            title: string
        """
        line = ''
        while not line.strip():
            line = my_file.readline()
            cls.offset += len(line)
        return line.strip()

    @classmethod
    def parse_file(cls, my_file, title):
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
        while title not in line:
            cls.offset += len(line)
            line = my_file.readline()
        while line:
            if line.strip():
                # if line has character
                match = reg.match(line)
                if match:
                    charac = match.group(1)
                pos_to_char[cls.offset] = charac
            cls.offset += len(line)
            line = my_file.readline()
        cls.pos_to_character_dicts.append(pos_to_char)

    @classmethod
    def run(cls, blob_key):
        """Open a zipfile and preprocess each of its text files.
        Args:
            blob_key: A blob key to a zip file containing one or more text files
        """
        cls.offset = 0
        blob_reader = blobstore.BlobReader(blob_key)
        with zipfile.ZipFile(blob_reader) as zip_files:
            for count, name in enumerate(zip_files.namelist()):
                with zip_files.open(name, 'r') as my_file:
                    title = self.find_title(my_file)
                    cls.ind_to_title[count] = cls.titlecase(title)
                    cls.parse_file(my_file, title)

    @classmethod
    def get_title(cls, index):
        """Get title of work.

        Args:
            index: index of file relative to zipfile passed to initializer

        Returns:
            title: a string with the capitalized title or None if index not
                found
        """
        if index >= len(cls.ind_to_title):
            raise FileIndexTooLargeError(len(cls.ind_to_title), index)
        return cls.ind_to_title[index]

    @classmethod
    def get_character(cls, index, offset):
        """Get character relative to a line.

        Args:
            index: index of file relative to zipfile passed to initializer
            offset: initial byte offset of line relative to the text file

        Returns:
            character: a string with the name of the character or empty string
                if the line is not pronounced by any character
        """
        if index >= len(cls.pos_to_character_dicts):
            raise FileIndexTooLargeError(len(cls.pos_to_character_dicts),
                                         index)
        pos_to_char = cls.pos_to_character_dicts[index]
        if offset in pos_to_char:
            return pos_to_char[offset]
        return ''
    
    @staticmethod
    def get_epilog_len(text, title):
        epilog_reg = re.compile(r'\s*' + title + '.*' + title)
        result = re.match(epilog_regex, text)
        epilog_len = result.span()[1]
        return epilog_len

    @staticmethod
    def get_speaks_offsets(body):
        char_reg = re.compile(r'^([A-Z].*)\t')
        offset_to_char = {}
        for match in char_reg.finditer(body)
            offset = match.start()
            character = match.group()
            offset_to_char[offset] = character


def preprocessing_map(data):
    """ """
    zipinfo, text_fn = data
    filename = zipinfo.filename
    ind = get_index(filename) # TODO
    text = text_fn()
    title = Preprocessing.find_title(text)
    offset = Preprocessing.get_epilog_len(text, title)
    body = text[offset:]
    offset_to_char = get_speaks_offsets(body)
    for key in offset_to_char:
        yield ind, str(key) + _SEP + offset_to_char[key]
    

    
    


    






    reg = re.compile(r'([^\s]+)\t.*$')
    charac = ''
    pos_to_char = {}
    title_not_found = True
    offset = 0
   
    for line in text.split('\n'):
        if title_not_found:
            if title in line:
                title_not_found = False
        else:
            if line.strip():
                match = reg.match(line)
                if match:
                    charac = match.group(1)
        
        offset += len(line) + 1 # +1 because of the removed \n


    
    line = my_file.readline()
    # Find title repeated
    while title not in line:
        cls.offset += len(line)
        line = my_file.readline()
    while line:
        if line.strip():
            # if line has character
            match = reg.match(line)
            if match:
                charac = match.group(1)
            pos_to_char[cls.offset] = charac
        cls.offset += len(line)
        line = my_file.readline()
    cls.pos_to_character_dicts.append(pos_to_char)


        


class PrePipeline(base_handler.PipelineBase):
    """A pipeline to run preprocessing.

    Args:
        blobkey: blobkey to process as string. Should be a zip archive with
            text files inside.
    """
    def run(self, filekey, blobkey):
        """Run the pipeline of the mapreduce job."""
        output = yield mapreduce_pipeline.MapreducePipeline(
                'preprocessing',
                'auxiliary.preprocessing.pre_map',
                'auxiliary.preprocessing.pre_reduce',
                'third_party.mapreduce.input_readers.BlobstoreZipLineInputReader',
                mapper_params={
                    'input_reader': {
                        'blob_keys': blobkey,
                    },
                },
                shards=16)
