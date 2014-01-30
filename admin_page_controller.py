#!/usr/bin/env python
#
# Copyright 2011 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" Handle the admin page, that allows to upload works.

An index that permits the rapid and easy retrieval of the lines in which a given
word is present is built. This index is built according to the following
structure:
    (word, work): line
This way whhen the user query for a word the results can be shown grouped by
work, giving a more pleasant view to the user.

This module was developed based on the mapreduce hello-world example, which is
available at
https://developers.google.com/appengine/docs/python/dataprocessing/helloworld.

"""

import datetime
import urllib
import logging
import jinja2
import re
import webapp2

# In order to allow the third party modules to be visible within themselves, it
# is required to add the third party path to sys.path
from third_party import add_third_party_path
add_third_party_path()

from google.appengine.ext import blobstore
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext.webapp import blobstore_handlers
from third_party.mapreduce import base_handler
from third_party.mapreduce import mapreduce_pipeline
from models.word import Word
from models.word_mentions_in_work import WordMentionsInWork
from resources.constants import Constants


from google.appengine.ext import ndb


class Parent(db.Model):
    """ A dumb parent class.

    This is just a stub to make the FileMetaData class have a parent. The parent
    is necessary to be able to perform ancestor queries, that can be put inside
    transactions. A transaction is needed to ensure data consistency when the
    results are queried.
    """
    pass


PARENT = Parent(key_name='parent')


class FileMetadata(db.Model):
    """A helper class that will hold metadata for the user's blobs.

    Specifially, we want to keep track of who uploaded it, where they uploaded
    it from (right now they can only upload from their computer, but in the
    future urlfetch would be nice to add), and links to the results of their MR
    jobs. To enable our querying to scan over our input data, we store keys in
    the form 'user/date/blob_key', where 'user' is the given user's e-mail
    address, 'date' is the date and time that they uploaded the item on, and
    'blob_key' indicates the location in the Blobstore that the item can be
    found at. '/' is not the actual separator between these values - we use '..'
    since it is an illegal set of characters for an e-mail address to contain.
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
    """A controller to the admin page.

    It handles the upload of works to the database. The map-reduce job is
    triggered on this page also."""

    template_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader('templates'), autoescape=True)

    @db.transactional
    def get(self):
        """Displays current zip files in the database mapreduce results."""

        results_query = FileMetadata.all()
        results_query.ancestor(PARENT)

        items = [result for result in results]
        indexed_items = []
        uploaded_items =[]
        for item in items:
            if item.index_link:
                indexed_items.append(item)
            else:
                uploaded_items.append(item)
        indexed_length = len(indexed_items)
        uploaded_length = len(uploaded_items)

        upload_url = blobstore.create_upload_url('/upload')

        self.response.out.write(self.template_env.get_template(
            "admin.html").render(
                {"username": 'admin',
                  "indexed_items": indexed_items,
                  "uploaded_items": uploaded_items,
                  "indexed_length": indexed_length,
                  "uploaded_length": uploaded_length,
                  "upload_url": upload_url}))

    def post(self):
        """Start map reduce job on selected file."""
        filekey = self.request.get("filekey")
        blob_key = self.request.get("blobkey")

        pipeline = IndexPipeline(filekey, blob_key)

        pipeline.start()
        #TODO(Caro): put a loading icon in the index link


def get_words(line):
    """Split a line into list of words."""
    line = re.sub(r'\W+', ' ', line)
    line = re.sub(r'[_0-9]+', ' ', line)
    return set(line.split())


def capitalize_as_title(title):
    """Formats the sentence to be capitalized as title"""
    return ' '.join(word[0].upper() + word[1:].lower() for word in
        title.split())


def get_title(text):
    """Get title of work (first non-empty line)."""
    title = ''
    for line in text.split('\n'):
        if line.strip():
            title = capitalize_as_title(line.strip())
            return title


SEP = '++'

def index_map(data):
    """Index map function.

    Args:
        data: Refers to a line from the input files. Is actually composed of a
            tuple (lineinfo, line). This is the return value from the
            ZipLineInputReader, available in the input readers of mapreduce.

    Yields:
        The map function must return a string, because that is what the reduce
        function expects. So, in order to simulate the return of a tuple (word,
        title), a string in the format {word}SEP{title} is returned. SEP is a
        separator constant.
    """
    (info, line) = data
    title = info[1]
    for word in get_words(line.lower()):
        yield (word + SEP + title, line)


def index_reduce(key, values):
    """Index reduce function.

    Args:
        key: a string in the format {word}SEP{work}
        values: the lines in which {word} appears in {work}

    """
    keys = key.split(SEP)
    word_value = keys[0]
    work_value = keys[1]
    word = Word.get_by_id(word_value)
    if not word:
        word = Word(id=word_value, name=word_value)
    
    mentions_in_work = WordMentionsInWork(parent=word.key, id=work_value, 
        title=work_value)
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


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    """Handler to upload data to blobstore."""

    def post(self):
        """Handle the upload of zipfiles that will later ve processed via map
        reduce."""
        source = 'uploaded by user'
        upload_files = self.get_uploads('file')
        blob_key = upload_files[0].key()
        name = self.request.get('name')

        user = users.get_current_user()

        username = 'admin'
        date = datetime.datetime.now()
        str_blob_key = str(blob_key)
        key = FileMetadata.get_key_name(username, date, str_blob_key)

        ctx = ndb.get_context()
        meta = FileMetadata(key_name=key, parent=PARENT)
        meta.owner = user
        meta.filename = name
        meta.uploaded_on = date
        meta.source = source
        meta.blobkey = str_blob_key
        meta.put()
        ctx.clear_cache()
        self.redirect('/admin')


class DownloadHandler(blobstore_handlers.BlobstoreDownloadHandler):
    """Handler to download blob by blobkey."""

    def get(self, key):
        """ Handle download of zip files and map reduce results."""
        key = str(urllib.unquote(key)).strip()
        logging.debug('key is %s', key)
        blob_info = blobstore.BlobInfo.get(key)
        self.send_blob(blob_info)

class ClearDatastoreHandler(webapp2.RequestHandler):
    """Handler to clear the datastore"""

    def get(self):
        """Clears the datastore."""
        db.delete(db.Query(keys_only=True))
        self.redirect('/admin')
