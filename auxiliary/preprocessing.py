""" A module to preprocess Shakespeare's works, gathering metadata."""
#TODO(izabela): treat files that do not follow the pattern

import zipfile
import re

from google.appengine.ext import blobstore
from third_party.mapreduce import base_handler
from third_party.mapreduce import mapreduce_pipeline

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


_SEP = '++'

class Preprocessing(object):
    """Preprocess Shakespeare's works to identify titles and characters.

        The preprocessing holds two important data strucutures. The first is a
        map(index, title) that relates the index of a text file (regarding its
        position in the zip file provided) to the title of the work it refers
        to. The second data structure is a list of maps. The i-th map is related
        to the i-th text file. Each map is of the form (offset, character), in
        which offset is the byte-offset of each line of text pronounced by a
        character.

        Attributes:
            ind_to_title: Dictionary that relates the index of a text file to
                the title of the work it refers to.
            pos_to_character_dicts: Dictionary that relates the index of a text
                file to the title of the work it refers to.

    """  
    pos_to_character_dicts = []
    ind_to_title = {}
    filename_to_ind = {}

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

    @staticmethod
    def find_title(text):
        print text
        title_reg = re.compile(r'\t([A-Z]+.*[A-Z])\s*$')
        print re.match(title_reg, text)
        title = re.match(title_reg, text).group(1)
        return title

    @staticmethod
    def get_speaks_offsets(body):
        char_reg = re.compile(r'^([A-Z].*)\t')
        offset_to_char = {}
        for match in char_reg.finditer(body):
            offset = match.start()
            character = match.group()
            offset_to_char[offset] = character

    @staticmethod
    def get_epilog_len(text, title):
        epilog_reg = re.compile(r'\s*' + title + '.*' + title)
        result = re.match(epilog_regex, text)
        epilog_len = result.span()[1]
        return epilog_len

    @staticmethod
    def preprocessing_map(data):
        """ """
        zipinfo, text_fn = data
        filename = zipinfo.filename
        ind = Preprocessing.get_index(filename)
        text = text_fn()
        title = Preprocessing.find_title(text)
        Preprocessing.ind_to_title[ind] = titlecase(title)
        offset = Preprocessing.get_epilog_len(text, title)
        body = text[offset:]
        offset_to_char = get_speaks_offsets(body)
        for key in offset_to_char:
            yield ind, str(key) + _SEP + offset_to_char[key]

    @staticmethod
    def preprocessing_reduce(key, values):
        pos_to_char_dict = {}
        for value in values:
            split = value.split(_SEP)
            offset = split[0]
            character = split[1]
            pos_to_char_dict[offset] = character
        Preprocessing.pos_to_char_dicts[key] = pos_to_char_dict

    @classmethod
    def build_name_to_ind(cls, blobkey):
        blob_reader = blobstore.BlobReader(blobkey)
        with zipfile.ZipFile(blob_reader) as zip_files:
            for count, name in enumerate(zip_files.namelist()):
                cls.filename_to_ind[name] = count

    @classmethod
    def get_index(cls, filename):
        if filename in cls.filename_to_ind:
            return cls.filename_to_ind[filename]
        #TODO(izabela): raise exception
        return ''

    @classmethod
    def run(cls, blobkey):
        cls.pos_to_char_dicts = {}
        cls.ind_to_title = {}
        cls.filename_to_ind = {}
        cls.build_name_to_ind(blobkey)
        pipeline =  PrePipeline(blobkey)
        pipeline.start()
    

class PrePipeline(base_handler.PipelineBase):
    """A pipeline to run preprocessing.

    Args:
        blobkey: blobkey to process as string. Should be a zip archive with
            text files inside.
    """
    def run(self, blobkey):
        """Run the pipeline of the mapreduce job."""
        output = yield mapreduce_pipeline.MapreducePipeline(
                'preprocessing',
                'auxiliary.preprocessing.Preprocessing.preprocessing_map',
                'auxiliary.preprocessing.Preprocessing.preprocessing_reduce',
                'third_party.mapreduce.input_readers.BlobstoreZipInputReader',
                mapper_params={
                    'input_reader': {
                        'blob_key': blobkey,
                    },
                },
                reducer_params={
                    'output_writer': {
                        'mime_type': 'text/plain',
                        'output_sharding': 'input',
                        'filesystem': 'blobstore',
                    },
                },
                shards=16)
        yield StoreOutput()


class StoreOutput(base_handler.PipelineBase):
    """A pipeline to store the result of the MapReduce job in the database.

    Args:
        encoded_key: the DB key corresponding to the metadata of this job
        output: the blobstore location where the output of the job is stored
    """

    def run(self):
        """ Store result of map reduce job."""
        pass














