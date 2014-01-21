class RegexFormatter(object):

    @classmethod
    def get_any_case_word_regex(cls, word):
        regex = ''
        formatted_text_list = []
        for letter in word:
            regex += '[' + letter + letter.upper() + ']'
        return regex
