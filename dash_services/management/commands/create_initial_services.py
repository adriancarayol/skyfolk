from django.core.management.base import BaseCommand, CommandError
from django.core.files.images import ImageFile
from dash_services.models import ServicesActivated
from django.db import IntegrityError
from skyfolk import th_settings
from django.contrib.staticfiles import finders


# List of description services
SERVICE_DESCRIPTION = {
    'ServiceReddit': "Conecta tu cuenta de Reddit con Skyfolk",
    'ServiceTwitter': "Conecta tu cuenta de Twitter con Skyfolk",
    'ServiceEvernote': "Conecta tu cuenta de Evernote con Skyfolk",
    'ServiceTumblr': "Conecta tu cuenta de Tumblr con Skyfolk",
}

# List of thumbnails of services
SERVICE_THUMBNAIL = {
    'ServiceReddit': finders.find('img/services/reddit.png'),
    'ServiceTwitter': finders.find('img/services/twitter.png'),
    'ServiceEvernote': finders.find('img/services/evernote.png'),
    'ServiceTumblr': finders.find('img/services/tumblr.png'),
}

class Command(BaseCommand):
    help = 'Create initial services if not exists'

    def handle(self, *args, **optinos):
        for index, service in enumerate(th_settings.TH_SERVICES):
            try:
                name_service = service.split('.')[-1]
                service = ServicesActivated.objects.create(name=name_service, status=True,
                    description=SERVICE_DESCRIPTION[name_service])
                service.thumbnail = ImageFile(open(SERVICE_THUMBNAIL[name_service], "rb"))
                service.save()
                self.stdout.write(self.style.SUCCESS('({}) Successfully created service {}').format(index, service))
            except (Exception, IntegrityError) as e:
                self.stdout.write(self.style.SUCCESS('({}) Error on created service {}: {}').format(index, service, e))
        
        self.stdout.write(self.style.SUCCESS('Create initial services DONE!'))
