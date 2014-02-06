'''This module is used charge to format the result from the database in order to
show it with bold tags between the searched word'''
import re

#Too few public methods (1/2) (too-few-public-methods)
#pylint: disable=R0903

class HTMLFormatter(object):
    '''Operations performed into a text in order format it as HTML'''

    @classmethod
    def apply_tag_to_pattern(cls, pattern, tag, text):
        '''Applies a tag into all ocurrences of a word in a given text.

        Args:
            pattern: Regex used to find the word in which the tag should be
                applied.
            tag: Tag to be applied. Ex: b for bolding.
            text: The text in which this processing is going to be executed.

        Returns:
            The text with the tag applied into the desired words.'''
        formatted_text = text
        matches = set(re.findall(pattern, text))
        for match in matches:
            formatted_text = re.sub(
                '\\b' + match + '\\b', '<%s>%s</%s>' % (tag, match, tag),
                formatted_text)
        return formatted_text
