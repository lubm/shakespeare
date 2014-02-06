""" A module to preprocess Shakespeare's works, gathering metadata."""
#TODO(izabela): treat files that do not follow the pattern

import zipfile
import re

from google.appengine.ext import blobstore
from mapreduce import base_handler
from mapreduce import mapreduce_pipeline

class FileIndexTooLargeError(Exception):
    """To be raised when a file index that does not exist is requested."""
    def __init__(self, num_files, index_requested):
        self.num_files = num_files
        self.ind_requested = index_requested

    def __str__(self):
        return '''Preprocessing only identified %d files in zipfile and %d file
            index was requested.''' % (self.num_files, self.ind_requested)


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
                This title is stripped (doesn't have any trailing spaces or
                front spaces).
                Examples: 'LOVE'S LABOUR'S LOST', 'OTHELLO'.

        Returns:
            This title but with only the first letter of each word capitalized.
        """
        return re.sub(r"[A-Za-z]+('[A-Za-z]+)?", lambda mo:
            mo.group(0)[0].upper() + mo.group(0)[1:].lower(), title)

    @staticmethod
    def find_title(text):
        """Get first non-empty line of a text."""
        title_reg = re.compile(r'\t([A-Z]+.*[A-Z])\s*\n')
        title = re.search(title_reg, text).group(1)
        return title

    @staticmethod
    def get_speaks_offsets(body):
        """Find offset in which each character starts to speak.
        
        Args:
            body: A string containing a work without the epilog (the section
            before the second appearance of the title).
        """
        char_reg = re.compile(r'(^|\n)([A-Z].*)\t')
        offset_to_char = {}
        for match in char_reg.finditer(body):
			offset = match.start(2)
			character = match.group(2)
			if not re.match('SCENE|ACT', character):
				offset_to_char[offset] = character
        return offset_to_char

    @staticmethod
    def get_epilog_len(text, title):
        """Get the length of the epilog.

        This functions expects text to contain a section encolsed between two
        appearances of the title, which we call epilog.

        Args:
            text: string containing a work
            title: a string containing the title the same way it is written in
                text. 
        """
        epilog_reg = re.compile(r'.*\t' + title + '.*\t' + title + '\s*\n', flags=re.DOTALL
                               )
        result = re.match(epilog_reg, text)
        epilog_len = result.span()[1]
        return epilog_len

    @staticmethod
    def preprocessing_map(data):
        """Mapper function to preprocessing task.
        
        Args:
            data: a tuple (zipinfo, text_fn), as it is returned from
                the ZipLineInputReader. Zipinfo is a zipfile.Zipinfo object and
                text_fn is a callable that returns the content of the file as a
                string.

        Yields:
            ind, value: ind is the index of the file being processed, inside the
                zipfile and value is a string of the form <offset>_SEP<character>.
                So, if (2, 100++HAMLET) is yielded it means that in the second file
                of the zipfile being processed, at the 100th byte, there is a
                speak by Hamlet.  
        """
        zipinfo, text_fn = data
        filename = zipinfo.filename
        ind = Preprocessing.get_index(filename)
        text = text_fn()
        title = Preprocessing.find_title(text)
        Preprocessing.ind_to_title[ind] = Preprocessing.titlecase(title)
        offset = Preprocessing.get_epilog_len(text, title)
        body = text[offset:]
        offset_to_char = Preprocessing.get_speaks_offsets(body)
        for key in offset_to_char:
            yield ind, str(key) + _SEP + offset_to_char[key]

    @staticmethod
    def preprocessing_reduce(key, values):
        """Reducing function of preprocessing.

        It builds a dictionary of dictionaries, indexed by file index. Each
        dictionary is of the type (offset, character).

        Args:
            key: the index of a file
            values: A list containing elements of the type
                <offset>_SEP<character>
        """
        pos_to_char_dict = {}
        for value in values:
            split = value.split(_SEP)
            offset = split[0]
            character = split[1]
            pos_to_char_dict[offset] = character
        Preprocessing.pos_to_char_dicts[key] = pos_to_char_dict

    @classmethod
    def build_name_to_ind(cls, blobkey):
        """Build a dictionary that maps filename to index.

        The dictionary maps the the name of each file inside the zipfile being
        processed to its relative position inside the zipfile.
        
        Args:
            blobkey: A blobkey to a zipfile containing one or more text files.
        """
        blob_reader = blobstore.BlobReader(blobkey)
        with zipfile.ZipFile(blob_reader) as zip_files:
            cls.filename_to_ind = {index: info.filename for (index, info) in
                                   enumerate(zip_files.infolist())}
    
    @classmethod
    def get_index(cls, filename):
        """Get index of file, relative to its position inside the zip file.

        Args:
            filename: A string containing the name of a file in the zipfile
            being processed.            
        """
        if filename in cls.filename_to_ind:
            return cls.filename_to_ind[filename]
        #TODO(izabela): raise exception
        return ''

    @classmethod
    def run(cls, blobkey):
        """Run the mapreduce job to preprocess the works.
        
        Args:
            blobkey: A blobkey to a zip file containing one or more text files.
        """
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
        yield mapreduce_pipeline.MapreducePipeline(
                'preprocessing',
                'auxiliary.preprocessing.Preprocessing.preprocessing_map',
                'auxiliary.preprocessing.Preprocessing.preprocessing_reduce',
                'mapreduce.input_readers.BlobstoreZipInputReader',
                mapper_params={
                    'input_reader': {
                        'blob_key': blobkey,
                    },
                },
                shards=16)

