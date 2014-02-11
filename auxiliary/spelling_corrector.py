'''Spelling Corrector module.

Contains functionality used to know, given a misspelled word, if there is any
correct word close to it. A word is considered close to another is they are
have distance 1.
'''
from models.word import Word

_ALPHABET = 'abcdefghijklmnopqrstuvwxyz'

def get_suggestion(word):
    '''Gets the most used suggestion for a misspelled word.

    The suggestion must exist in the database and must have distance 1 to the
    input word.

    There is more than one suggestion at distance 1 that exists in the database,
    it chooses the one that appears the database.

    Args:
        word: misspelled word.

    Returns:
        A suggestion of this word for the user or None if it doesn't find any.
    '''
    if Word.get_by_id(word):
        return None
    
    candidates = _get_candidates(_words_edit_distance_one(word))
    best_count = 0
    suggestion = None
    for candidate in candidates:
        if candidate.count > best_count:
            best_count = candidate.count
            suggestion = candidate
    if suggestion:
        return suggestion.name
    return None

def _splits(word):
    '''Convert a word into a list of tuples of all the possible splits of it.

    Example:
    _splits('love') = [('', 'love'), ('l', 'ove'), ('lo', 've'), ('lov', 'e'),
        ('love', '')]
    '''
    return [(word[:split_index], word[split_index:])
        for split_index in range(len(word) + 1)]

def _deletes(list_of_splited_words):
    '''Deletes a letter in all the second elements in the list of splited words.

    Allways deletes the first element in the second element of the tuple for
    each word.
    '''
    return [first_part + second_part[1:]
        for first_part, second_part in list_of_splited_words if second_part]

def _transposes(list_of_splited_words):
    '''Swaps 2 letters of the splited words in the list.

    The ones that swaps are the last character of the first element of the tuple
    with the first character of the second element in the tuple.'''
    transposes = []
    for beg, ending in list_of_splited_words:
        if len(ending) > 1:
            transposes.append(beg + ending[1] + ending[0] + ending[2:])
    return transposes

def _replaces(list_of_splited_words):
    '''Replaces one letter for the words in the list.

    Deletes the first character in the second element of the tuple and adds a
    new word to the result with this character replaced by other letter in the
    alphabet.'''
    return [a + c + b[1:]
        for a, b in list_of_splited_words for c in _ALPHABET if b]

def _inserts(list_of_splited_words):
    '''Adds an extra letter in the middle of all the words in the list'''
    return [a + c + b
        for a, b in list_of_splited_words for c in _ALPHABET]

def _words_edit_distance_one(word):
    '''Creates a set of all the strings that are at distance 1 of the word
    given.

    The generated strings are not allways valid words.

    For generating them it calls _deletes, _transposes, _replaces and _inserts,
    for all the possible splits of a word.

    Words A and B are at distance 1 if A can be transformed into B doing only
    one insertion, deletion, swap or replacement of characters.
    '''
    splits = _splits(word)

    deletes = _deletes(splits)
    transposes = _transposes(splits)
    replaces = _replaces(splits)
    inserts = _inserts(splits)

    return set(deletes + transposes + replaces + inserts)

def _get_candidates(words):
    '''Given all the words at distance 1 filters the words that are not present
    in the database and therefore not valid.'''
    known_words = []
    for word in words:
        word_from_database = Word.get_by_id(word)

        if word_from_database:
            known_words.append(word_from_database)
    return known_words
