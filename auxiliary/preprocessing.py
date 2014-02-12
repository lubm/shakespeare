""" A module to preprocess Shakespeare's works and build an index."""

# Disable error 'too many public methods' error, due to inheritance
#pylint: disable=R0904

import logging
import re
import zipfile
import json
import bisect
import pickle

from google.appengine.ext import blobstore
from mapreduce import base_handler
from mapreduce import context
from mapreduce import mapreduce_pipeline
from mapreduce.lib import pipeline

from models.character import Character
from models.line import Line
from models.word import Word
from models.work import Work


class FileIndexTooLargeError(Exception):
    """To be raised when a file index that does not exist is requested."""
    def __init__(self, num_files, index_requested):

        self.num_files = num_files
        self.ind_requested = index_requested
        Exception.__init__(self, self.__repr__())

    def __str__(self):
        return '''Preprocessing only identified %d files in zipfile and %d file
            index was requested.''' % (self.num_files, self.ind_requested)


_SEP = '+'

class Preprocessing(object):
    """Preprocess Shakespeare's works to identify titles and characters.

        The preprocessing holds four data strucutures. The first is a
        map(index, title) that relates the index of a text file (regarding its
        position in the zip file provided) to the title of the work it refers
        to.

        The second data structure is a map of maps. The map indexed
        by the key i is related to the i-th text file. Each map is of the form
        (offset, character), in which offset is the byte-offset of each line of
        text pronounced by a character.

        The third data structure is a map(filename, index) that relates the name
        of a file in the zip to its position inside the zip.

        The fourth data structure is a map of lists. The map indexed by the key
        i is related to the i-th file. Each list contains the sorted keys of the
        respective i-th dictionary in the pos_to_character_dicts data structure.
        These lists are useful for computations that requires sorting these keys
        and that are performed many times (in the function get_character).

        Attributes:
            ind_to_title: Dictionary that relates the index of a text (integer)
                file to the title of the work it refers to.
            pos_to_character_dicts: Dictionary of dictionaries indexed by file
                index (integer). Each dictionary relates an offset in a file to
                a character.
            filename_to_ind: Dictionary that relates a string with the name of a
                file inside the zip to its index (integer) in the zip file.

    """
    ind_to_title = {}
    pos_to_character_dicts = {}
    filename_to_ind = {}
    ind_to_sorted_offsets = {}

    @staticmethod
    def get_character(char_map, sorted_offsets, offset):
        """Get character relative to a line.

        Args:
            char_maps: dict of dicts that relates a file index to a dict of the
                type (offset, character).
            ind_to_sorted_offsets: dicts that relates a file index to sorted
                list of the offsets of the respective map in the previous
                structure.
            index: index of file relative to zipfile passed to the initializer.
            offset: initial byte offset of line relative to the text file.

        Returns:
            character: a string with the name of the character or 'EPILOG' if
            the line is part of the epilog.

        TODO(izabela): fix behavior for lines that indicate stage behavior.
            Right now the previous character who pronounced anything is
            returned.
        """

        #Find closest smaller offset in which a character starts a speak
        aux = bisect.bisect(sorted_offsets, offset) - 1
        if aux >= 0:
            closest_offset = sorted_offsets[aux]
            return char_map[str(closest_offset)]
        return 'EPILOG'

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
        title_reg = re.compile(r'\t([A-Z0-9]+.*[A-Z])\s*\n')
        title = re.search(title_reg, text).group(1)
        return title

    @staticmethod
    def get_speaks_offsets(body, epilog_len):
        """Find offset in which each character starts to speak.

        Args:
            body: A string containing a work without the epilog (the section
                before the second appearance of the title).
            epilog_len: The length in bytes of the epilog.
        """
        char_reg = re.compile(r'(^|\n)([A-Z].*)\t')
        offset_to_char = {}
        for match in char_reg.finditer(body):
            offset = match.start(2) + epilog_len
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
        epilog_reg = re.compile(r'.*?\t' + title + '.*?\t' + title + r'\s*\n',
            flags=re.DOTALL)
        result = re.match(epilog_reg, text)
        if result == None:
            return None
        epilog_len = result.span()[1]
        return epilog_len

    @staticmethod
    def map(data):
        """Mapper function to preprocessing task.

        Args:
            data: a tuple (zipinfo, text_fn), as it is returned from
                the ZipLineInputReader. Zipinfo is a zipfile.Zipinfo object and
                text_fn is a callable that returns the content of the file as a
                string.

        Yields:
            ind_and_title, value: ind_and_title is a string of the form
                <index>_SEP<title> and value is a string of the form
                <offset>_SEP<character>.

            Example:

                If (2++HAMLET, 100++BERNARNDO) is yielded it means that the
                second file of the zipfile is entitled 'HAMLET' and at the 100th
                byte there is a speak pronounced by BERNARNDO.
        """
        zipinfo, text_fn = data
        filename = zipinfo.filename
        ind = Preprocessing.get_index(filename)
        text = text_fn()
        title = Preprocessing.find_title(text)
        epilog_len = Preprocessing.get_epilog_len(text, title)
        if epilog_len == None:
            yield str(ind) + _SEP + title, '0' + _SEP + ''
        else:
            body = text[epilog_len:]
            offset_to_char = Preprocessing.get_speaks_offsets(body, epilog_len)
            if len(offset_to_char) == 0:
                yield str(ind) + _SEP + title, '0' + _SEP + ''
            for key in offset_to_char:
                yield str(ind) + _SEP + title, str(key) + _SEP + \
                    offset_to_char[key]

    @staticmethod
    def reduce(key, values):
        """Reducing function of preprocessing.

        It builds a dictionary of dictionaries, indexed by file index. Each
        dictionary is of the type (offset, character).

        Args:
            key: the index of a file
            values: A list containing elements of the type
                <offset>_SEP<character>
        """
        pos_to_char_dict = {}
        index, title = key.split(_SEP)
        metadata = {'title': title}
        #Preprocessing.ind_to_title[int(index)] = title
        for value in values:
            split = value.split(_SEP)
            offset, character = split
            pos_to_char_dict[int(offset)] = character
        #Preprocessing.pos_to_character_dicts[int(index)] = pos_to_char_dict
        metadata['pos_to_char'] = pos_to_char_dict
        metadata['sorted_offsets'] = sorted(pos_to_char_dict.keys())
        #Preprocessing.ind_to_sorted_offsets[int(index)] = \
            #sorted(pos_to_char_dict.keys())\
        yield index + _SEP + json.dumps(metadata) + '\n'


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
            cls.filename_to_ind = {info.filename: index for (index, info) in
                                   enumerate(zip_files.infolist())}

    @classmethod
    def get_index(cls, filename):
        """Get index of file, relative to its position inside the zip file.

        Args:
            filename: A string containing the name of a file in the zipfile
                being processed.
        """
        ctx = context.get()
        filename_to_ind = \
            ctx.mapreduce_spec.mapper.params[u'metadata'][u'filename_to_ind']
        if filename in filename_to_ind:
            return filename_to_ind[filename]
        logging.error('PROBLEM: could not find filename in index')
        return None

def run(blobkey):
    """Run the mapreduce job to preprocess the works.

    Args:
        blobkey: A blobkey to a zip file containing one or more text files.
    """
    Preprocessing.pos_to_character_dicts = {}
    Preprocessing.ind_to_title = {}
    Preprocessing.filename_to_ind = {}
    Preprocessing.ind_to_sorted_offsets = {}
    Preprocessing.build_name_to_ind(blobkey)
    pipeline =  PrePipeline(blobkey, Preprocessing.filename_to_ind)
    pipeline.start()
    logging.info('Starting preprocessing pipeline.')
    logging.info ('Pipeline information available at %s/status?root=%s',
                  pipeline.base_path, pipeline.pipeline_id) 


class PrePipeline(base_handler.PipelineBase):
    """A pipeline to run preprocessing.

    Args:
        blobkey: blobkey to process as string. Should be a zip archive with
            text files inside.
    """
    def __init__(self, blobkey, filename_to_ind) :
        super(PrePipeline, self).__init__(blobkey, filename_to_ind)
        self.blobkey = blobkey

    def run(self, blobkey, filename_to_ind):
        """Run the pipeline of the mapreduce job."""
        metadata = yield mapreduce_pipeline.MapreducePipeline(
            'preprocessing',
            'auxiliary.preprocessing.Preprocessing.map',
            'auxiliary.preprocessing.Preprocessing.reduce',
            'mapreduce.input_readers.BlobstoreZipInputReader',
            'mapreduce.output_writers.BlobstoreOutputWriter',
            mapper_params={
                'input_reader': {
                    'blob_key': blobkey
                },
                'metadata': {
                    'filename_to_ind': filename_to_ind,
                }
            },
            reducer_params={
                'mime_type': 'text/plain'
            },
            shards=16)
        #with pipeline.After(metadata):
        #yield StoreOutput("Phrases", filekey, output)
        yield mapreduce_pipeline.MapreducePipeline(
            'index',
            'auxiliary.preprocessing.IndexBuild.map',
            'auxiliary.preprocessing.IndexBuild.reduce',
            'mapreduce.input_readers.BlobstoreZipLineInputReader',
            'mapreduce.output_writers.BlobstoreOutputWriter',
            mapper_params = (yield MapperParams(blobkey, metadata)),
            shards=16)


    def finalized(self):
        logging.info('********** Index built succesfully :) ***********')

class MapperParams(base_handler.PipelineBase):
    
    def run(self, blobkey, metadata):
        return {'input_reader': {'blob_keys': blobkey}, 'metadata': metadata}


class IndexBuild(object):
    """Build index containing mentions of the words.

    This class holds all the methods related to the build of the index that is
    the holds the core data of the search engine. The index is indexed by word,
    but each instance of word also holds metadata about its originating work and
    the character who mentioned it (if applicable).

    The build of the index happens via a mapreduce job.
    """
    @staticmethod
    def get_words(line):
        """Split a line into list of words."""
        line = re.sub(r'\W+', ' ', line)
        line = re.sub(r'[_0-9]+', ' ', line)
        return line.split()

    @staticmethod
    def map(data):
        """Index map function.

        Args:
            data: Refers to a line from the input files. It is actually composed
            of a tuple (lineinfo, line). This is the return value from the
            ZipLineInputReader, available among the input readers of mapreduce.

        Yields:
            The map function must return a string, because that is what the
            reduce function expects. So, in order to simulate the return of a
            tuple (word, title), a string in the format <word>_SEP<word> is
            returned. _SEP is a separator constant.
        """
        info, line = data
        if line.strip() == '':
            return
        _, file_index, offset = info
        ctx = context.get()
        params = ctx.mapreduce_spec.mapper.params
        metadata_blob = params['metadata']
        blob_reader = blobstore.BlobReader(metadata_blob[0].split('/')[-1])
        files_info = blob_reader.read().split('\n')[:-1] # the last one is empty
        for info in files_info:
            index, serial_dict = info.split(_SEP)
            if index == str(file_index):
                metadata = json.loads(serial_dict)
                break
        char_map = metadata['pos_to_char']
        sorted_offsets = metadata['sorted_offsets']
        character = Preprocessing.get_character(char_map, sorted_offsets,
                                                offset)
        title = metadata['title']
        line_db = Line(line=line)
        line_key = line_db.put()
        for word in IndexBuild.get_words(line.lower()):
            yield (word + _SEP + title + _SEP + character,
                            pickle.dumps(line_key))

    @staticmethod
    def reduce(key, values):
        """Index reduce function.
        Args:
            key: a string in the format {word}_SEP{work}
            values: the lines in which {word} appears in {work}

        """
        keys = key.split(_SEP)
        word_value, work_value, char_value = keys
        word = Word.get_by_id(word_value)
        work_titlecase = Preprocessing.titlecase(work_value)
        if not word:
            word = Word(id=word_value, name=word_value, count=len(values))
            work = Work(parent=word.key, id=work_titlecase,
                            title=work_titlecase, count=len(values))
        else:
            word.count += len(values)
            work = Work.get_by_id(work_titlecase, parent=word.key)
            if work:
                work.count += len(values)
            else:
                work = Work(parent=word.key, id=work_titlecase,
                    title=work_titlecase, count=len(values))
        character_titlecase = Preprocessing.titlecase(char_value)
        char = Character(parent=work.key, id=character_titlecase,
            name=character_titlecase, count= len(values))
        for line in set(values):
            char.mentions.append(pickle.loads(line))
        word.put()
        work.put()
        char.put()


class IndexPipeline(base_handler.PipelineBase):
    """A pipeline to run Index.

    Args:
        blobkey: blobkey to process as string. Should be a zip archive with
            text files inside.
    """
    def run(self, blobkey, ind_to_title, pos_to_char_dicts,
            ind_to_sorted_offsets):
        """Run the pipeline of the mapreduce job."""
        yield mapreduce_pipeline.MapreducePipeline(
                'index',
                'auxiliary.preprocessing.IndexBuild.map',
                'auxiliary.preprocessing.IndexBuild.reduce',
                'mapreduce.input_readers.BlobstoreZipLineInputReader',
                'mapreduce.output_writers.BlobstoreOutputWriter',
                mapper_params={
                    'input_reader': {
                        'blob_keys': blobkey,
                    },
                    'metadata': {
                        'ind_to_title': ind_to_title,
                        'pos_to_char_dicts': pos_to_char_dicts,
                        'ind_to_sorted_offsets': ind_to_sorted_offsets
                    }
                },
                shards=16)

    def finalized(self):
        logging.info('Indexing pipeline finished succesfully.')

