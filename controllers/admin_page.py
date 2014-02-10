#!/usr/bin/env python

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

from google.appengine.ext import blobstore
from google.appengine.ext import db
from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.ext.webapp import blobstore_handlers

from models.character import Character
from models.file_metadata import FileMetadata
from models.line import Line
from models.word import Word
from models.work import Work
from auxiliary.preprocessing import Preprocessing
from resources.constants import Constants
import auxiliary.preprocessing as database_creation

class Parent(db.Model):
    """ A dumb parent class.

    This is just a stub to make the FileMetaData class have a parent. The parent
    is necessary to be able to perform ancestor queries, that can be put inside
    transactions. A transaction is needed to ensure data consistency when the
    results are queried.
    """
    pass


_PARENT = Parent(key_name='parent')


class AdminPageController(webapp2.RequestHandler):
    """A controller to the admin page.

    It handles the upload of works to the database. The map-reduce job is
    triggered on this page also.

    """

    template_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader('templates'), autoescape=True)

    @db.transactional
    def get(self):
        """Displays current zip files in the database mapreduce results."""

        results_query = FileMetadata.all()
        results_query.ancestor(_PARENT)

        items = [result for result in results_query]
        indexed_items = []
        uploaded_items = []
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
        blob_key = self.request.get("blobkey")

        database_creation.run(blob_key)


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
        meta = FileMetadata(key_name=key, parent=_PARENT)
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
        ndb.delete_multi(Word.query().fetch(keys_only=True))
        ndb.delete_multi(Work.query().fetch(keys_only=True))
        ndb.delete_multi(Character.query().fetch(keys_only=True))
        ndb.delete_multi(Line.query().fetch(keys_only=True))
        db.delete(FileMetadata.all(keys_only=True).run())
        self.redirect('/admin')
