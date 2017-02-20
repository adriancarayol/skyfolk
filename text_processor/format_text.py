# Clase que dado un texto,
# lo devuelve formateado (con hashtags, menciones y emoticonos)
import re

from django.contrib.auth.models import User

from emoji import Emoji
from notifications.signals import notify
from celery.utils.log import get_task_logger
from skyfolk.celery import app
from django.core.exceptions import ObjectDoesNotExist

logger = get_task_logger(__name__)

class TextProcessor():
    def __get_mentions_text(emitter, text):
        menciones = re.findall('\\@[a-zA-Z0-9_]+', text)
        print('Len antes: {}'.format(len(menciones)))
        menciones = set(menciones)
        print('Len despues: {}'.format(len(menciones)))
        for mencion in menciones:
            if User.objects.filter(username=mencion[1:]):
                try:
                    recipientprofile = User.objects.get(username=mencion[1:])
                except ObjectDoesNotExist:
                    continue

                privacity = recipientprofile.profile.is_visible(emitter.profile, emitter.pk)
                if privacity and privacity != 'all':
                    continue

                if emitter.pk != recipientprofile.pk:
                    notify.send(emitter, actor=emitter.username,
                            recipient=recipientprofile,
                            verb=u'¡te ha mencionado en su tablón!',
                            description='Mencion')

                text = text.replace(mencion,
                                    '<a href="/profile/%s">%s</a>' %
                                    (mencion[1:], mencion))
        return text

    def __get_hashtags_text(text, hashtags):
        for hashtag in hashtags:
            text = text.replace(hashtag,
                                '<a href="/search/">{0}</a>'.format(hashtag))
        return text

    @classmethod
    def get_format_text(cls, text, emitter, hashtags=None):
        formatText = Emoji.replace(text)
        formatText = cls.__get_hashtags_text(formatText, hashtags)
        formatText = cls.__get_mentions_text(emitter, formatText)
        formatText = formatText.replace('\n', '').replace('\r', '')
        return formatText


