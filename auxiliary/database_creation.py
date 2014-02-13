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


_SEP = '+'


def run(blobkey):
    """Run mapreduce pipelines to build the word index.
    
    Run the mapreduce jobs to preprocess the works and then build an index
    that relates a word alog with it respective work and character to a mention
    (line) in one of the files of the blob_key.

    Args:
        blobkey: A blobkey to a zip file containing one or more text files.
    """
    filename_to_ind = build_name_to_ind(blobkey)
    pipeline =  CreateIndexPipeline(blobkey, filename_to_ind)
    pipeline.start()
    logging.info('Starting preprocessing pipeline.')
    logging.info ('Pipeline information available at %s/status?root=%s',
                  pipeline.base_path, pipeline.pipeline_id) 


def get_character(char_map, sorted_offsets, offset):
    """Get character relative to a line.

    Args:
        char_map: dict that relates a byte offset to the name of a character
        sorted_offsets: sorted list of the keys in the char_map dict.
        offset: initial byte offset of a line in the text file.

    Returns:
        character: a string with the name of the character or 'EPILOG' if
        the line is part of the epilog.

    Example:
        Consider that char_map = {30: 'ANA', 7: 'BEATRIZ', 45: 'MARCO'}. This
        means that the respective text file has character speaks starting at the
        byte offsets 30, 7 and 45, and that these speaks are from Ana, Beatriz
        and Marco, respectively.

        If the character for the offset 32 is requested, this function will
        return 'ANA', because this is the closest smaller offset.

    TODO(izabela): fix behavior for lines that indicate stage behavior of
        characters. Right now the previous character who pronounced anything
        is returned.
    """

    #Find closest smaller offset via binary search
    aux = bisect.bisect(sorted_offsets, offset) - 1
    if aux >= 0:
        closest_offset = sorted_offsets[aux]
        return char_map[str(closest_offset)]
    return 'EPILOG'


def titlecase(title):
    """Capitalize first letter of each word.

    Args:
        title: A string to be capitalized as title.

    Returns:
        The title with only the first letter of each word capitalized.
    
    Example: 'LOVE'S LABOUR'S LOST' returns 'Love's Labour's Lost'.
    """
    return re.sub(r"[A-Za-z]+('[A-Za-z]+)?", lambda mo:
        mo.group(0)[0].upper() + mo.group(0)[1:].lower(), title)


def find_title(text):
    """Get first non-empty line of a text."""
    title_reg = re.compile(r'\t([A-Z0-9]+.*[A-Z])\s*\n')
    title = re.search(title_reg, text).group(1)
    return title


def get_speaks_offsets(body, epilog_len):
    """Find offset in which each character starts to speak.

    Args:
        body: A string composed of a sequence of character speaks that are in
            the form <CHARACTER>\t<SPEAK>  
        epilog_len: The length in bytes of the epilog. Basically, anything that
            happens to be before the character speaks and therefore should be
            stripped out before calling this function. The length is necessary
            to the calculation of the offset to be correct, regarding the start
            of the text file.
    
    Returns:
        offset_to_char: a map of the type {offset: character}. 
    """
    char_reg = re.compile(r'(^|\n)([A-Z].*)\t')
    offset_to_char = {}
    for match in char_reg.finditer(body):
        offset = match.start(2) + epilog_len
        character = match.group(2)
        if not re.match('SCENE|ACT', character):
            offset_to_char[offset] = character
    return offset_to_char


def get_epilog_len(text, title):
    """Get the length of the epilog.

    This function expects text to contain a section enclosed between two
    appearances of <title>, which we call epilog. This section does not follow
    the same part of the rest and stripping it makes the parsing of the file
    easier.

    Args:
        text: string containing a work
        title: a string containing the title the same way it is written in
            text.

    Returns:
        epilog_len, if text is a play and therefore contains an epilog, or None,
            otherwise.
    """
    epilog_reg = re.compile(r'.*?\t' + title + '.*?\t' + title + r'\s*\n',
        flags=re.DOTALL)
    result = re.match(epilog_reg, text)
    if result == None:
        return None
    epilog_len = result.span()[1]
    return epilog_len


def pre_map(data):
    """Mapper function to preprocessing task.

    Args:
        data: a tuple (zipinfo, text_fn), as it is returned from
            the ZipLineInputReader. Zipinfo is a zipfile.Zipinfo object and
            text_fn is a callable that returns the content of the file as a
            string.

    Yields:
        ind, value: ind_and_title is a string of the form <index> and value is a
            string of the form <title_SEP><offset>_SEP<character>.

        Example:

            If (2, HAMLET++100++BERNARNDO) is yielded it means that the
            second file of the zipfile is entitled 'HAMLET' and at the 100th
            byte there is a speak pronounced by BERNARNDO.
    """
    zipinfo, text_fn = data
    filename = zipinfo.filename
    ind = get_index(filename)
    text = text_fn()
    title = find_title(text)
    epilog_len = get_epilog_len(text, title)
    if epilog_len == None:
        yield str(ind), title + _SEP + '0' + _SEP + ''
    else:
        body = text[epilog_len:]
        offset_to_char = get_speaks_offsets(body, epilog_len)
        if len(offset_to_char) == 0:
            yield str(ind), title + _SEP + '0' + _SEP + ''
        for key in offset_to_char:
            yield str(ind), title + _SEP + str(key) + _SEP + \
                offset_to_char[key]


def pre_reduce(index, values):
    """Reducing function of preprocessing.

    It builds a dictionary of dictionaries, indexed by file index. Each
    dictionary is of the type (offset, character).

    Args:
        key: the index of a file
        values: A list containing elements of the type
            <title>_SEP<offset>_SEP<character>
    """
    pos_to_char_dict = {}
    for value in values:
        title, offset, character = value.split(_SEP)
        pos_to_char_dict[int(offset)] = character
    metadata = {'title': title}
    metadata['pos_to_char'] = pos_to_char_dict
    metadata['sorted_offsets'] = sorted(pos_to_char_dict.keys())
    yield index + _SEP + json.dumps(metadata) + '\n'


def build_name_to_ind(blobkey):
    """Build a dictionary that maps filename to index.

    The dictionary maps the the name of each file inside the zipfile being
    processed to its relative position inside the zipfile.

    Args:
        blobkey: A blobkey to a zipfile containing one or more text files.
    """
    blob_reader = blobstore.BlobReader(blobkey)
    with zipfile.ZipFile(blob_reader) as zip_files:
        filename_to_ind = {info.filename: index for (index, info) in
                               enumerate(zip_files.infolist())}
        return filename_to_ind


def get_index(filename):
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
    logging.error('Could not find filename in index')
    return None


class CreateIndexPipeline(base_handler.PipelineBase):
    """A pipeline to run preprocessing.

    Args:
        blobkey: blobkey to process as string. Should be a zip archive with
            one or more text files and nothing else.
    """
    def run(self, blobkey, filename_to_ind):
        """Run the pipeline of the mapreduce job."""
        metadata = yield mapreduce_pipeline.MapreducePipeline(
            'preprocessing',
            'auxiliary.database_creation.pre_map',
            'auxiliary.database_creation.pre_reduce',
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
            shards=43)
        yield mapreduce_pipeline.MapreducePipeline(
            'index',
            'auxiliary.database_creation.index_map',
            'auxiliary.database_creation.index_reduce',
            'mapreduce.input_readers.BlobstoreZipLineInputReader',
            'mapreduce.output_writers.BlobstoreOutputWriter',
            mapper_params = (yield MapperParams(blobkey, metadata)),
            shards=200)


    def finalized(self):
        logging.info('***********  Index built succesfully  ***********')


class MapperParams(base_handler.PipelineBase):
    """A wrapper to mapper_params.

    This wrapper is needed to be able to pass the dict metadata as a
    mapper_param to the mapreduce pipeline.
    """    
    def run(self, blobkey, metadata):
        return {'input_reader': {'blob_keys': blobkey}, 'metadata': metadata}


def get_words(line):
    """Split a line into list of words."""
    line = re.sub(r'\W+', ' ', line)
    line = re.sub(r'[_0-9]+', ' ', line)
    return line.split()


def select_metadata(all_metadata, file_index):
    """"Select metadata of respective file index among all metadata.
    
    Args:
        all_metadata: A list of strings in the format <index>_SEP<serial_dict>,
        in which <serial_dict> is a serialized dictionary containing all the
        metadata associated to <index>.
    
    Returns:  The respective dict desirialized.
    """
    metadata = None
    for data in all_metadata:
        index, serial_dict = data.split(_SEP)
        if index == str(file_index):
            metadata = json.loads(serial_dict)
            break
    if metadata == None:
        logging.error('File index not found in metadata dictionary.')
    return metadata


def index_map(data):
    """Index map function.

    Args:
        data: Refers to a line from the input files. It is actually composed
        of a tuple (lineinfo, line). This is the return value from the
        ZipLineInputReader, available among the input readers of mapreduce.

    Yields:
        A tuple in the format <word>_SEP<title>_SEP<character>,
        <serial_line_key>.
        line_key needs to be serialized because it is an object and reduce
        expects strings as input.
    """
    info, line = data
    if line.strip() == '':
        return
    _, file_index, offset = info
    ctx = context.get()
    params = ctx.mapreduce_spec.mapper.params
    metadata_blob = params['metadata']
    blob_reader = blobstore.BlobReader(metadata_blob[0].split('/')[-1])
    all_meta = blob_reader.read().split('\n')[:-1] # the last one is empty
    metadata = select_metadata(all_meta, file_index)
    char_map = metadata['pos_to_char']
    sorted_offsets = metadata['sorted_offsets']
    character = get_character(char_map, sorted_offsets, offset)
    title = metadata['title']
    line_db = Line(line=line)
    line_key = line_db.put()
    for word in get_words(line.lower()):
        yield (word + _SEP + title + _SEP + character, pickle.dumps(line_key))


def index_reduce(key, values):
    """Index reduce function.
    Args:
        key: a string in the format <word>_SEP<work>_SEP<character>
        values: the lines in which <word> appears in <work> in a speak of
            <character>

    The word is either added to the database or updated with its new occurence,
    adding info about the work in which it was found, which character pronounced
    it (if applicable), a count of occurrences and a reference to the line in
    which it was found.
    """
    keys = key.split(_SEP)
    word_value, work_value, char_value = keys
    word = Word.get_by_id(word_value)
    work_titlecase = titlecase(work_value)
    character_titlecase = titlecase(char_value)
    work = None
    
    if word:
        word.count += len(values)
        work = Work.get_by_id(word_value + work_titlecase)
    else:
        word = Word(id=word_value, name=word_value, count=len(values))

    if work:
        work.count += len(values)
    else:
        work = Work(id=word_value + work_titlecase, title=work_titlecase, 
            count=len(values))
        word.works.append(work.key)
    
    char = Character(id=word_value + work_titlecase + character_titlecase,
        name=character_titlecase, count=len(values))
    work.characters.append(char.key)
    char.mentions = [pickle.loads(like_key) for like_key in set(values)]
    
    word.put()
    work.put()
    char.put()

