""" TODO(izabela): module docstring """

import zipfile
import re
import sys


class Preprocessing(object):
    
    pos_to_character_dicts = []
    ind_to_title = {}
    offset = 0

    def titlecase(self, title):
        return re.sub(r"[A-Za-z]+('[A-Za-z]+)?", lambda mo:
            mo.group(0)[0].upper() + mo.group(0)[1:].lower(), title)

    def get_title(self, my_file):
        line = ''
        while not line.strip():
            line = my_file.readline()
            self.offset += len(line)
        return self.titlecase(line.strip())
        

    def parse_file(self, my_file, title):
        """
        Returns:
            (epilog, speakings): A string representing the epilog and an
                iterable containing each speaking block.

        """
        charac = ''
        pos_to_char = {}
        line = my_file.readline()
        # Find title repeated
        while title not in line:
            offset += len(line)
            line = my_file.readline()
        while line:
            if line.strip():
                # if line has character
                if '\t' in line:
                    charac = re.split('\t', speaking)[0]
                else:
                    offset += len(line)
                    epilog += line
                    line = my_file.readline()
                pos_to_char[offset] = charac
            offset += len(line)
        pos_to_char_dicts.append(pos_to_char)


    def process_file(self, my_file, ind):
        pos_to_character = {}
        title = self.get_title(my_file)
        print title
        self.ind_to_title[ind] = title
        epilog, speakings = self.parse_file(my_file, title)
        offset = len(epilog)
        for block in speakings:
            char = self.find_character(block)
            print char
            for line in block:
                pos_to_character[offset] = char
                offset += len(line)
        self.pos_to_character_dicts.append(pos_to_character)


    def run(self, file_path):
        with zipfile.ZipFile(file_path, 'r') as zip_files:
            for count, name in enumerate(zip_files.namelist()):
                with zip_files.open(name, 'r') as my_file:
                    self.process_file(my_file, count)


p = Preprocessing()
p.run('static/text.zip')

    
