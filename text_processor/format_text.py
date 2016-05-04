# Clase que dado un texto, lo devuelve formateado (con hashtags, menciones y emoticonos)
from emoji import Emoji
import re
from django.contrib.auth.models import User

class TextProcessor():
    def __get_mentions_text(text):
        menciones = re.findall('\\@[a-zA-Z0-9_]+', text)
        for mencion in menciones:
            if User.objects.filter(username=mencion[1:]):
                text = text.replace(mencion,
                                    '<a href="/profile/%s">%s</a>' % (mencion[1:], mencion))
        return text
    def __get_hashtags_text(text):
        hashtags = re.findall('#[a-zA-Z][a-zA-Z0-9_]*', text)
        for hashtag in hashtags:
            text = text.replace(hashtag,
            '<a href="/search/">%s</a>' % (hashtag))
        return text

    @classmethod
    def get_format_text(cls, text):
        formatText = Emoji.replace(text)
        formatText = cls.__get_hashtags_text(formatText)
        formatText = cls.__get_mentions_text(formatText)
        return formatText
