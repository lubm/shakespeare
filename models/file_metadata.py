from google.appengine.ext import db

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
