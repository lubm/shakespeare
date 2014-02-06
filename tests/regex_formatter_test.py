import unittest

from auxiliary.formatter import RegexFormatter

class RegexGeneration(unittest.TestCase):

    def test_generate_regex_for_capital_case_word(self):
        self.assertEqual(RegexFormatter.get_any_case_word_regex('HELLO'),
            '\\b[hH][eE][lL][lL][oO]\\b')

    def test_generate_regex_for_lower_case_word(self):
        self.assertEqual(RegexFormatter.get_any_case_word_regex('hello'),
            '\\b[hH][eE][lL][lL][oO]\\b')

    def test_generate_regex_for_mixed_case_word(self):
        self.assertEqual(RegexFormatter.get_any_case_word_regex('HeLlo'),
            '\\b[hH][eE][lL][lL][oO]\\b')

    def test_does_not_fail_with_empty_string(self):
        self.assertEqual(RegexFormatter.get_any_case_word_regex(''),
            '\\b\\b')

   