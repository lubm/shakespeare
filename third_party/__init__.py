import os
import sys

def add_third_party_path():
    third_party_directory = os.path.dirname(os.path.abspath(__file__))
    if third_party_directory not in sys.path:
        sys.path.insert(0, third_party_directory)
