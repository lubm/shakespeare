""" This module handles the admin page, in which it is possible to upload fles.

The text files are processed via mapreduce and an index is built. 
"""

#TODO: Explain better the index in the docstring above

import time
import datetime
import jinja2
import re
import webapp2

from google.appengine.ext import blobstore
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext.webapp import blobstore_handlers
from mapreduce import base_handler
from mapreduce import mapreduce_pipeline

class FileMetadata(db.Model):
    """A helper class that will hold metadata for the user's blobs.

    Specifially, we want to keep track of who uploaded it, where they uploaded it
    from (right now they can only upload from their computer, but in the future
    urlfetch would be nice to add), and links to the results of their MR jobs. To
    enable our querying to scan over our input data, we store keys in the form
    'user/date/blob_key', where 'user' is the given user's e-mail address, 'date'
    is the date and time that they uploaded the item on, and 'blob_key'
    indicates the location in the Blobstore that the item can be found at. '/'
    is not the actual separator between these values - we use '..' since it is
    an illegal set of characters for an e-mail address to contain.
    """

    __SEP = ".."
    __NEXT = "./"

    owner = db.UserProperty()
    filename = db.StringProperty()
    uploadedOn = db.DateTimeProperty()
    source = db.StringProperty()
    blobkey = db.StringProperty()
    index_link = db.StringProperty()


    @staticmethod
    def getKeyName(username, date, blob_key):
        """Returns the internal key for a particular item in the database.

        Our items are stored with keys of the form 'user/date/blob_key' ('/' is
        not the real separator, but __SEP is).

        Args:
            username: The given user's e-mail address.
            date: A datetime object representing the date and time that an input
                file was uploaded to this app.
            blob_key: The blob key corresponding to the location of the input file
                in the Blobstore.
        Returns:
            The internal key for the item specified by (username, date, blob_key).
        """

        sep = FileMetadata.__SEP
        return str(username + sep + str(date) + sep + blob_key)


class AdminPageController(webapp2.RequestHandler):
    
    template_env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"),
                                                                        autoescape=True)

    def get(self):
        #user = users.get_current_user()
        #username = user.nickname()

        results = FileMetadata.all()

        items = [result for result in results]
        length = len(items)

        upload_url = blobstore.create_upload_url("/upload")

        self.response.out.write(self.template_env.get_template("admin.html").render(
                {"username": 'admin',
                  "items": items,
                  "length": length,
                  "upload_url": upload_url}))

    def post(self):
        filekey = self.request.get("filekey")
        blob_key = self.request.get("blobkey")

        pipeline = IndexPipeline(filekey, blob_key)

        pipeline.start()
        #TODO: put a loading icon in the index link
        print 'returned from pipeline.start()'
        print 'pipeline: %s', pipeline
        self.redirect("/admin")


def split_into_words(s):
    """Split a sentence into list of words."""
    s = re.sub(r"\W+", " ", s)
    s = re.sub(r"[_0-9]+", " ", s)
    return s.split()


def index_map(data):
    """Index map function."""
    (entry, text_fn) = data
    text = text_fn()

    for l in text.split("\n"):
        for w in split_into_words(l.lower()):
            yield (w, l)


def index_reduce(key, values):
    """Index reduce function."""
    yield "%s: %s\n" % (key, list(set(values)))


class IndexPipeline(base_handler.PipelineBase):
    """A pipeline to run Index demo.

    Args:
        blobkey: blobkey to process as string. Should be a zip archive with
            text files inside.
    """


    def run(self, filekey, blobkey):
        print 'Run IndexPipeline ************'
        output = yield mapreduce_pipeline.MapreducePipeline(
                "index",
                "admin_page_controller.index_map",
                "admin_page_controller.index_reduce",
                "mapreduce.input_readers.BlobstoreZipInputReader",
                "mapreduce.output_writers.BlobstoreOutputWriter",
                mapper_params={
                    "input_reader": {
                        "blob_key": blobkey,
                    },
                },
                reducer_params={
                    "output_writer": {
                        "mime_type": "text/plain",
                        "output_sharding": "input",
                        "filesystem": "blobstore",
                    },
                },
                shards=16)
        print 'End of IndexPipeline ************'
        yield StoreOutput("Index", filekey, output)


class StoreOutput(base_handler.PipelineBase):
    """A pipeline to store the result of the MapReduce job in the database.

    Args:
        mr_type: the type of mapreduce job run (e.g., WordCount, Index)
        encoded_key: the DB key corresponding to the metadata of this job
        output: the blobstore location where the output of the job is stored
    """

    def run(self, mr_type, encoded_key, output):
        key = db.Key(encoded=encoded_key)
        m = FileMetadata.get(key)
        m.index_link = output[0]
        m.put()

        
class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    """Handler to upload data to blobstore."""

    def post(self):
        source = "uploaded by user"
        upload_files = self.get_uploads("file")
        blob_key = upload_files[0].key()
        name = self.request.get("name")

        user = users.get_current_user()

        username = 'admin'
        date = datetime.datetime.now()
        str_blob_key = str(blob_key)
        key = FileMetadata.getKeyName(username, date, str_blob_key)

        m = FileMetadata(key_name = key)
        m.owner = user
        m.filename = name
        m.uploadedOn = date
        m.source = source
        m.blobkey = str_blob_key
        m.put()
        time.sleep(5)
        self.redirect("/admin")


    

