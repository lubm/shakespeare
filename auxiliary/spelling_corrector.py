import re
import collections

from models.word import Word

class SpellingCorrector(object):
    def __init__(self):
        self.alphabet = 'abcdefghijklmnopqrstuvwxyz'


    def splits(self, word):
        return [(word[:split_index], word[split_index:]) 
            for split_index in range(len(word) + 1)]


    def deletes(self, list_of_splited_words):
        return [first_part + second_part[1:] 
            for first_part, second_part in list_of_splited_words if second_part]

    def transposes(self, list_of_splited_words):
        transposes = []
        for first_part, second_part in list_of_splited_words:
            if len(second_part) > 1:
                new_element = first_part + second_part[1] + second_part[0] + second_part[2:]
                transposes.append(new_element)
        return transposes

    def replaces(self, list_of_splited_words):
        return [a + c + b[1:] 
            for a, b in list_of_splited_words for c in self.alphabet if b]

    def inserts(self, list_of_splited_words):
        return [a + c + b
            for a, b in list_of_splited_words for c in self.alphabet]
            

    def words_edit_distance_one(self, word):
        splits = self.splits(word)

        deletes = self.deletes(splits)
        transposes = self.transposes(splits)
        replaces = self.replaces(splits)
        inserts = self.inserts(splits)

        return set(deletes + transposes + replaces + inserts)

    def get_candidates(self, words): 
        known_words = []
        for word in words:
            word_from_database = Word.get_by_id(word)
            if word_from_database:
                known_words.append(word_from_database)
        return known_words

    def get_suggestion(self, word):
        if Word.get_by_id(word):
            return None

        candidates = self.get_candidates(self.words_edit_distance_one(word))
        best_count = 0
        suggestion = None
        for candidate in candidates:
            if candidate.count > best_count:
                best_count = candidate.count
                suggestion = candidate
        if suggestion:
            return suggestion.name
        return None
