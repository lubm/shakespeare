""" A module to preprocess Shakespeare's works, gathering metadata."""
#TODO(izabela): treat files that do not follow the pattern

import logging
import re
import zipfile

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
    pos_to_character_dicts = {}
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
        #Find closest smaller offset in which a character starts a speak
        closest_offset = bisect.bisect(sorted(pos_to_char.keys()))
        return pos_to_char[offset]

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
        epilog_reg = re.compile(r'.*?\t' + title + '.*?\t' + title + '\s*\n', 
			flags=re.DOTALL)
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
        print '********************************'
        print ind
        print '********************************'
        text = text_fn()
        title = Preprocessing.find_title(text)
        print title
        Preprocessing.ind_to_title[ind] = Preprocessing.titlecase(title)
        print Preprocessing.ind_to_title[ind]
        offset = Preprocessing.get_epilog_len(text, title)
        print offset
        body = text[offset:]
        offset_to_char = Preprocessing.get_speaks_offsets(body)
        print offset_to_char
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
        print '*REDUCE*******************************'
        print key
        print '********************************'
        pos_to_char_dict = {}
        for value in values:
            split = value.split(_SEP)
            offset = split[0]
            character = split[1]
            pos_to_char_dict[offset] = character
        Preprocessing.pos_to_character_dicts[int(key)] = pos_to_char_dict

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
        if filename in cls.filename_to_ind:
            return cls.filename_to_ind[filename]
        #TODO(izabela): raise exception
        return ''

    @classmethod
    def run(cls, blobkey, filekey):
        """Run the mapreduce job to preprocess the works.
        
        Args:
            blobkey: A blobkey to a zip file containing one or more text files.
        """
        cls.pos_to_character_dicts = {}
        cls.ind_to_title = {}
        cls.filename_to_ind = {}
        cls.build_name_to_ind(blobkey)
        pipeline =  PrePipeline(blobkey, filekey)
        pipeline.start()
    

class PrePipeline(base_handler.PipelineBase):
    """A pipeline to run preprocessing.

    Args:
        blobkey: blobkey to process as string. Should be a zip archive with
            text files inside.
    """
    def __init__(self, blobkey, filekey):
        super(PrePipeline, self).__init__(blobkey, filekey)
        self.blobkey = blobkey
        self.filekey = filekey

    def run(self, blobkey, filekey):
        """Run the pipeline of the mapreduce job."""
        pipeline = yield mapreduce_pipeline.MapreducePipeline(
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

    def finalized(self):
        logging.info('Preprocessing finished succesfully')
        print Preprocessing.pos_to_character_dicts
        print '**************************'
        print Preprocessing.ind_to_title
        print '**************************'
        print Preprocessing.filename_to_ind
        print '**************************'
        #pipeline = IndexPipeline(self.filekey, self.blobkey)
        #pipeline.start()


def get_words(line):
    """Split a line into list of words."""
    line = re.sub(r'\W+', ' ', line)
    line = re.sub(r'[_0-9]+', ' ', line)
    return set(line.split())


_SEP = '++'

def index_map(data):
    """Index map function.

    Args:
        data: Refers to a line from the input files. Is actually composed of a
            tuple (lineinfo, line). This is the return value from the
            ZipLineInputReader, available in the input readers of mapreduce.

    Yields:
        The map function must return a string, because that is what the reduce
        function expects. So, in order to simulate the return of a tuple (word,
        title), a string in the format {word}_SEP{title} is returned. SEP is a
        separator constant.
    """
    info, line = data
    logging.info(info)
    _, file_index, offset = info
    print Preprocessing.ind_to_title
    title = Preprocessing.get_title(file_index)
    character = Preprocessing.get_character(file_index, offset)
    logging.info('LINE: %s', line)
    logging.info(title)
    logging.info(character)
    for word in get_words(line.lower()):
        yield (word + _SEP + title + _SEP + character, line)


def index_reduce(key, values):
    """Index reduce function.

    Args:
        key: a string in the format {word}_SEP{work}
        values: the lines in which {word} appears in {work}

    """
    keys = key.split(_SEP)
    word_value = keys[0]
    work_value = keys[1]
    word = Word.get_by_id(word_value)
    if not word:
        word = Word(id=word_value, name=word_value)
    
    work = Work(parent=word.key, id=work_value, title=work_value)

    char_value = "Dummy Character" # TODO: CHANGE
    char = Character(parent=work.key, id=char_value, name=char_value)
    
    for line in values:
        char.mentions.append(line)
    
    word.put()
    work.put()
    char.put()
    yield '%s: %s\n' % (key, list(set(values)))


class IndexPipeline(base_handler.PipelineBase):
    """A pipeline to run Index.

    Args:
        blobkey: blobkey to process as string. Should be a zip archive with
            text files inside.
    """
    def run(self, filekey, blobkey):
        """Run the pipeline of the mapreduce job."""
        output = yield mapreduce_pipeline.MapreducePipeline(
                'index',
                'auxiliary.preprocessing.index_map',
                'auxiliary.preprocessing.index_reduce',
                'mapreduce.input_readers.BlobstoreZipLineInputReader',
                'mapreduce.output_writers.BlobstoreOutputWriter',
                mapper_params={
                    'input_reader': {
                        'blob_keys': blobkey,
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
        yield StoreOutput(filekey, output)


class StoreOutput(base_handler.PipelineBase):
    """A pipeline to store the result of the MapReduce job in the database.

    Args:
        encoded_key: the DB key corresponding to the metadata of this job
        output: the blobstore location where the output of the job is stored
    """

    def run(self, encoded_key, output):
        """ Store result of map reduce job."""
        key = db.Key(encoded=encoded_key)
        meta = FileMetadata.get(key)
        meta.index_link = output[0]
        meta.put()
