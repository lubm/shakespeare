import re

class HTMLFormatter(object):

    @classmethod
    def apply_tag_to_pattern(cls, pattern, tag, text):
        formatted_text = text
        matches = set(re.findall(pattern, text))
        for match in matches:
            formatted_text = re.sub('\\b' + match + '\\b', '<%s>%s</%s>' % (tag, match, tag), formatted_text)
        return formatted_text
