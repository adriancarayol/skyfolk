# Clase que dado un texto,
# lo devuelve formateado (con hashtags, menciones y emoticonos)
import re
from emoji import Emoji
from django.contrib.auth.models import User
from notifications.signals import notify


class TextProcessor():
    def __get_mentions_text(emitter, text):
        menciones = re.findall('\\@[a-zA-Z0-9_]+', text)
        for mencion in menciones:
            if User.objects.filter(username=mencion[1:]):
                recipientprofile = User.objects.get(username=mencion[1:])
                if emitter.pk != recipientprofile.pk:
                    notify.send(emitter, actor=emitter.username,
                                recipient=recipientprofile,
                                verb=u'¡te ha mencionado en su tablón!',
                                description='Mencion')
                text = text.replace(mencion,
                                    '<a href="/profile/%s">%s</a>' %
                                    (mencion[1:], mencion))
        return text

    def __get_hashtags_text(text):
        hashtags = re.findall('#[a-zA-Z][a-zA-Z0-9_]*', text)
        for hashtag in hashtags:
            text = text.replace(hashtag,
                                '<a href="/search/">%s</a>' % (hashtag))
        return text

    @classmethod
    def get_format_text(cls, text, emitter):
        formatText = Emoji.replace(text)
        formatText = cls.__get_hashtags_text(formatText)
        formatText = cls.__get_mentions_text(emitter, formatText)
        return formatText
