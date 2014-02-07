# TODO(luciana): After changing the function to javascript, adapt the code  

import unittest

import auxiliary.formatter as formatter

class NumberOfOccurencesTest(unittest.TestCase):
    one_word_values = [
        ('\\b[hH][eE][lL][lL][oO]\\b',
         'You say goodbye and I say hello.',
         'You say goodbye and I say <tag>hello</tag>.'),
        ('\\b[hH][oO][lL][dD]\\b',
         'I wanna hold your hand!',
         'I wanna <tag>hold</tag> your hand!'),
        ('\\b[pP][lL][eE][aA][sS][eE]\\b',
         'Please, say to me',
         '<tag>Please</tag>, say to me')]

    multiple_words_values = [
        ('\\b[hH][eE][lL][lL][oO]\\b',
         'You say goodbye and I say hello. Hello, hello!',
         'You say goodbye and I say <tag>hello</tag>. <tag>Hello</tag>, <tag>hello</tag>!'),
        ('\\b[hH][oO][lL][dD]\\b',
         'I wanna hold your hand! I wanna hold hold hold your hand.',
         'I wanna <tag>hold</tag> your hand! I wanna <tag>hold</tag> <tag>hold</tag> <tag>hold</tag> your hand.'),
        ('\\b[pP][lL][eE][aA][sS][eE]\\b',
         'Please, please, please! Say to me! Please',
         '<tag>Please</tag>, <tag>please</tag>, <tag>please</tag>! Say to me! <tag>Please</tag>')]

    no_word_values = [
        ('\\b[aA][nN][yY]\\b',
         'You say goodbye and I say hello.',
         'You say goodbye and I say hello.'),
        ('\\b[wW][aA][iI][tT]\\b',
         'I wanna hold your hand!',
         'I wanna hold your hand!'),
        ('\\b[hH][eE][yY]\\b',
         'Please, say to me',
         'Please, say to me')]

    def test_one_word(self):
        """Test the formatting of dummy tags around word patterns in the text with one word"""
        for pattern, text, expected_result in self.one_word_values:
            actual_result = formatter.apply_tag_to_pattern(pattern, 'tag', text)
            self.assertEqual(expected_result, actual_result)

    def test_multiple_words(self):
        """Test the formatting of dummy tags around word patterns in the text with multiple words"""
        for pattern, text, expected_result in self.multiple_words_values:
            actual_result = formatter.apply_tag_to_pattern(pattern, 'tag', text)
            self.assertEqual(expected_result, actual_result)

    def test_no_word(self):
        """Test the formatting of dummy tags around word patterns in the text with no word"""
        for pattern, text, expected_result in self.no_word_values:
            actual_result = formatter.apply_tag_to_pattern(pattern, 'tag', text)
            self.assertEqual(expected_result, actual_result)

class CaseTest(unittest.TestCase):
    lower_case_values = [
        ('\\b[dD][oO]\\b',
         'What are you going to do?',
         'What are you going to <tag>do</tag>?'),
        ('\\b[hH][aA][pP][pP][yY]\\b',
         'I fell happy inside!',
         'I fell <tag>happy</tag> inside!'),
        ('\\b[yY][oO][uU]\\b',
         'Call me whenever you need.',
         'Call me whenever <tag>you</tag> need.')]

    upper_case_values = [
        ('\\b[dD][oO]\\b',
         'What are you going to DO?',
         'What are you going to <tag>DO</tag>?'),
        ('\\b[hH][aA][pP][pP][yY]\\b',
         'I fell HAPPY inside!',
         'I fell <tag>HAPPY</tag> inside!'),
        ('\\b[yY][oO][uU]\\b',
         'Call me whenever YOU need.',
         'Call me whenever <tag>YOU</tag> need.')]

    mixed_case_values = [
        ('\\b[dD][oO]\\b',
         'What are you going to Do?',
         'What are you going to <tag>Do</tag>?'),
        ('\\b[hH][aA][pP][pP][yY]\\b',
         'I fell HaPPy inside!',
         'I fell <tag>HaPPy</tag> inside!'),
        ('\\b[yY][oO][uU]\\b',
         'Call me whenever yOu need.',
         'Call me whenever <tag>yOu</tag> need.')]

    def testLowerCase(self):
        """Test the formatting of dummy tags around word patterns in the text with the word in lower case"""
        for pattern, text, expected_result in self.lower_case_values:
            actual_result = formatter.apply_tag_to_pattern(pattern, 'tag', text)
            self.assertEqual(expected_result, actual_result)

    def testUpperCase(self):
        """Test the formatting of dummy tags around word patterns in the text with the word in lower case"""
        for pattern, text, expected_result in self.upper_case_values:
            actual_result = formatter.apply_tag_to_pattern(pattern, 'tag', text)
            self.assertEqual(expected_result, actual_result)

    def testMixedCase(self):
        """Test the formatting of dummy tags around word patterns in the text with the word in lower case"""
        for pattern, text, expected_result in self.mixed_case_values:
            actual_result = formatter.apply_tag_to_pattern(pattern, 'tag', text)
            self.assertEqual(expected_result, actual_result)


class WordWithinAnotherTest(unittest.TestCase):
    values = [
        ('\\b[dD][oO]\\b',
         'What are you going to do? I look forward to the new doodle.',
         'What are you going to <tag>do</tag>? I look forward to the new doodle.'),
        ('\\b[iI][nN]\\b',
         'I fell HaPPy inside! You will find it in there. Keep looking!',
         'I fell HaPPy inside! You will find it <tag>in</tag> there. Keep looking!'),
        ('\\b[dD][rR][yY]\\b',
         'Do not forget to do the laundry or your clothes will not dry in time!',
         'Do not forget to do the laundry or your clothes will not <tag>dry</tag> in time!')]

    def testWordWithinAnother(self):
        """Test the formatting of dummy tags around word patterns in the text with the word inside another"""
        for pattern, text, expected_result in self.values:
            actual_result = formatter.apply_tag_to_pattern(pattern, 'tag', text)
            self.assertEqual(expected_result, actual_result)

class RegexGeneration(unittest.TestCase):

    def test_generate_regex_for_capital_case_word(self):
        self.assertEqual(formatter.get_any_case_word_regex('HELLO'),
            '\\b[hH][eE][lL][lL][oO]\\b')

    def test_generate_regex_for_lower_case_word(self):
        self.assertEqual(formatter.get_any_case_word_regex('hello'),
            '\\b[hH][eE][lL][lL][oO]\\b')

    def test_generate_regex_for_mixed_case_word(self):
        self.assertEqual(formatter.get_any_case_word_regex('HeLlo'),
            '\\b[hH][eE][lL][lL][oO]\\b')

    def test_does_not_fail_with_empty_string(self):
        self.assertEqual(formatter.get_any_case_word_regex(''),
            '\\b\\b')


if __name__ == '__main__':
    unittest.main()
