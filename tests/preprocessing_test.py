import unittest

from auxiliary.preprocessing import Preprocessing
import os

class PreprocessingTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_titleize(self):
        title = Preprocessing.titlecase("A LOVER'S COMPLAINT")
        self.assertEqual(title, "A Lover's Complaint")

        title2 = Preprocessing.titlecase("THE TEMPEST")
        self.assertEqual(title2, "The Tempest")

        title3 = Preprocessing.titlecase("TWELFTH NIGHT")
        self.assertEqual(title3, "Twelfth Night")

    def test_get_title_of_a_file_without_spaces(self):
        file_to_read = open('workfile', 'w')
        file_to_read.write('HAMLET')
        file_to_read.close()

        file_to_read = open('workfile', 'r')
        preprocessor = Preprocessing('80')

        title = preprocessor.get_title(file_to_read)
        self.assertEqual(title, 'HAMLET')
        self.assertEqual(6, preprocessor.offset)

        #Move into 6 characters after the offset to see if the title is there
        file_to_read.seek(preprocessor.offset - 6)
        self.assertEqual(file_to_read.read(6), "HAMLET")

        os.remove("workfile")

    def test_get_title_of_a_file_with_spaces(self):
        file_to_read = open('workfile', 'w')
        file_to_read.write('\n \tVENUS AND ADONIS \t')
        file_to_read.close()

        file_to_read = open('workfile', 'r')
        preprocessor = Preprocessing('80')

        title = preprocessor.get_title(file_to_read)
        self.assertEqual(title, 'VENUS AND ADONIS')
        self.assertEqual(23, preprocessor.offset)

        #Move into 6 characters after the offset to see if the title is there
        file_to_read.seek(preprocessor.offset - 16)
        self.assertEqual(file_to_read.read(16), "VENUS AND ADONIS")

        os.remove("workfile")





