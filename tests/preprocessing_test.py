import unittest

from auxiliary.preprocessing import Preprocessing
import os

class PreprocessingTest(unittest.TestCase):

    def test_find_title(self):
        text = u'''\tJORGE

                JORGE
    ANA Jorge I (Hanover, 28 de maio de 1660 Osnabruque, 11 de junho
    de 1727) foi o Rei da GraBretanha e Irlanda de 1 de
    agosto de 1714 at sua morte, e tambem governante do Ducado e
    Eleitorado de
               II.'''
        title = Preprocessing.find_title(text)
        self.assertEqual('JORGE', title)


if __name__ == '__main__':
    unittest.main()



