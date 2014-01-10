import os
import re

class Parser(object):

    def __init__(self, data_dir):
        self.data_dir = data_dir
        if self.data_dir[-1] != '/':
            self.data_dir += '/'
        self.index = {}

    def parse(self):
        print self.data_dir
        for file_name in os.listdir(self.data_dir):
            print file_name
            data_file = open(self.data_dir + file_name, 'r')
            for line in data_file:
                line = line.strip()
                if line:
                    words = re.sub('[^\w]', ' ', line).split()
                    for word in words:
                        if word not in self.index:
                            self.index[word] = []
                        self.index[word].append((line, file_name))


if __name__ == '__main__':
    parser = Parser('test')
    parser.parse()
    print parser.index
