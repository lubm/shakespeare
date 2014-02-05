import re
import collections

from models.word import Word

class SpellingCorrector(object):
  def __init__(self):
    self.alphabet = 'abcdefghijklmnopqrstuvwxyz'

  def edits1(self, word):
    splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes    = [a + b[1:] for a, b in splits if b]
    transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
    replaces   = [a + c + b[1:] for a, b in splits for c in self.alphabet if b]
    inserts    = [a + c + b     for a, b in splits for c in self.alphabet]
    return set(deletes + transposes + replaces + inserts)

  def known_edits2(self, word):
    return set(e2 for e1 in self.edits1(word) for e2 in self.edits1(e1) if e2 in Word.all())

  def known_words(self, words): 
    known_words = []
    for word in words:
      if Word.get_by_id(word):
        known_words.append(word)
    return known_words

  def correct(self, word):
    candidates = self.known_words([word]) or self.known_words(self.edits1(word)) or self.known_edits2(word) or [word]
    return max(candidates, key=Word.all())