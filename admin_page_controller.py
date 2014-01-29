""" This module handles the admin page, in which it is possible to upload fles.

The text files are processed via mapreduce and an index is built.
"""

#TODO(izabela): Explain better the index in the docstring above

import time
import datetime
import urllib
import logging
import jinja2
import re
import webapp2

from google.appengine.ext import blobstore
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext.webapp import blobstore_handlers
from mapreduce import base_handler
from mapreduce import mapreduce_pipeline
from models.word import Word
from models.word_mentions_in_work import WordMentionsInWork
from resources.constants import Constants

from google.appengine.ext import ndb

class FileMetadata(db.Model):
    """A helper class that will hold metadata for the user's blobs.

    Specifially, we want to keep track of who uploaded it, where they
    uploaded it from (right now they can only upload from their compu-
    ter, but in the future urlfetch would be nice to add), and links
    to the results of their MR jobs. To enable our querying to scan over
    our input data, we store keys in the form 'user/date/blob_key',
    where 'user' is the given user's e-mail address, 'date' is the date
    and time that they uploaded the item on, and 'blob_key' indicates the
    location in the Blobstore that the item can be found at. '/' is not
    the actual separator between these values - we use '..' since it is
    an illegal set of characters for an e-mail address to contain.
    """

    __SEP = '..'
    __NEXT = './'

    owner = db.UserProperty()
    filename = db.StringProperty()
    uploaded_on = db.DateTimeProperty()
    source = db.StringProperty()
    blobkey = db.StringProperty()
    index_link = db.StringProperty()


    @staticmethod
    def get_key_name(username, date, blob_key):
        """Returns the internal key for a particular item in the database.

        Our items are stored with keys of the form 'user/date/blob_key' ('/' is
        not the real separator, but __SEP is).

        Args:
            username: The given user's e-mail address.
            date: A datetime object representing the date and time that an input
                file was uploaded to this app.
            blob_key: The blob key corresponding to the location of the input
                file in the Blobstore.
        Returns:
            The internal key for the item specified by
                (username, date, blob_key).
        """

        sep = FileMetadata.__SEP
        return str(username + sep + str(date) + sep + blob_key)


class AdminPageController(webapp2.RequestHandler):
    """A controller to the admin page, that handles the upload of works to the
    database. The map-reduce job is triggered on this page also."""

    template_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader("templates"), autoescape=True)

    def get(self):
        """Displays current zip files loaded to the database and correspondant
        results after map reduce."""
        #user = users.get_current_user()
        #username = user.nickname()

        results = FileMetadata.all()

        items = [result for result in results]
        length = len(items)

        upload_url = blobstore.create_upload_url('/upload')

        self.response.out.write(self.template_env.get_template(
            "admin.html").render(
                {"username": 'admin',
                  "items": items,
                  "length": length,
                  "upload_url": upload_url}))

    def post(self):
        """Start map reduce job on selected file."""
        filekey = self.request.get("filekey")
        blob_key = self.request.get("blobkey")

        pipeline = IndexPipeline(filekey, blob_key)

        pipeline.start()
        #TODO(Caro): put a loading icon in the index link
        self.redirect("/admin")


def get_words(sentence):
    """Split a sentence into list of words."""
    sentence = re.sub(r"\W+", " ", sentence)
    sentence = re.sub(r"[_0-9]+", " ", sentence)
    return set(sentence.split())


def capitalize_as_title(title):
    """Formats the sentence to be capitalized as title"""
    return [' '.join(word[0].upper() + word[1:].lower() for word in
        title.split())]


def get_title(text):
    """Get title of work (first non-empty line)."""
    title = ''
    for line in text.split('\n'):
        if line.strip():
            title = capitalize_as_title(line.strip())
            return title


def index_map(data):
    """Index map function."""
    (_, text_fn) = data
    text = text_fn()
    title = get_title(text)
    for line in text.split('\n'):
        for word in get_words(line.lower()):
            yield (word + '++' + title, line)


def index_reduce(key, values):
    """Index reduce function."""
    keys = key.split('++')
    word_id = keys[0]
    work_id = keys[1]
    
    word = Word.get_by_id(word_id)
    if not word:
        word = Word(id=word_id, name=word_id)
    
    mentions_in_work = WordMentionsInWork(parent=word.key, id=work_id, 
        title=work_id)
    mentions_in_work.mentions = []

    for line in values:
        mentions_in_work.mentions.append(line)
    
    word.put()
    mentions_in_work.put()
    
    yield '%s: %s\n' % (key, list(set(values)))


class IndexPipeline(base_handler.PipelineBase):
    """A pipeline to run Index demo.

    Args:
        blobkey: blobkey to process as string. Should be a zip archive with
            text files inside.
    """


    def run(self, filekey, blobkey):
        """Run the pipeline of the mapreduce job."""
        output = yield mapreduce_pipeline.MapreducePipeline(
                'index',
                'admin_page_controller.index_map',
                'admin_page_controller.index_reduce',
                'mapreduce.input_readers.BlobstoreZipInputReader',
                'mapreduce.output_writers.BlobstoreOutputWriter',
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
        yield StoreOutput("Index", filekey, output)


class StoreOutput(base_handler.PipelineBase):
    """A pipeline to store the result of the MapReduce job in the database.

    Args:
        encoded_key: the DB key corresponding to the metadata of this job
        output: the blobstore location where the output of the job is stored
    """

    def run(self, mr_type, encoded_key, output):
        #TODO(izabela): Find a way to remove mr_type without breaking the code
        """ Store result of map reduce job."""
        key = db.Key(encoded=encoded_key)
        meta = FileMetadata.get(key)
        meta.index_link = output[0]
        meta.put()


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    """Handler to upload data to blobstore."""

    def post(self):
        """Handle the upload of zipfiles that will later ve processed via map
        reduce."""
        source = "uploaded by user"
        upload_files = self.get_uploads("file")
        blob_key = upload_files[0].key()
        name = self.request.get("name")
        #TODO(izabela): handle empty string better

        user = users.get_current_user()

        username = 'admin'
        date = datetime.datetime.now()
        str_blob_key = str(blob_key)
        key = FileMetadata.get_key_name(username, date, str_blob_key)

        meta = FileMetadata(key_name = key)
        meta.owner = user
        meta.filename = name
        meta.uploaded_on = date
        meta.source = source
        meta.blobkey = str_blob_key
        meta.put()
        time.sleep(2)
        #TODO(izabela): Replace the sleep with waiting for completion
        self.redirect("/admin")


class DownloadHandler(blobstore_handlers.BlobstoreDownloadHandler):
    """Handler to download blob by blobkey."""

    def get(self, key):
        """ Handle download of zip files and map reduce results."""
        key = str(urllib.unquote(key)).strip()
        logging.debug("key is %s", key)
        blob_info = blobstore.BlobInfo.get(key)
        self.send_blob(blob_info)

class ClearDatastoreHandler(webapp2.RequestHandler):
    """Handler to clear the datastore"""

    def get(self):
        """Clears the datastore."""
        db.delete(db.Query(keys_only=True))
        self.redirect('/admin')
