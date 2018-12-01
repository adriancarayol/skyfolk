from django import template
from external_services.twitter.twitter_service import TwitterService
from external_services.instagram.instagram_service import InstagramService
from external_services.youtube.youtube_service import YouTubeService


register = template.Library()

external_services = {
    'twitter': TwitterService,
    'instagram': InstagramService,
    'youtube': YouTubeService,
}


@register.filter(name='get_auth_url_given_service_name')
def get_auth_url_given_service_name(service_name):
    if not service_name:
        return '/'

    service_name = service_name.lower()
    service = external_services.get(service_name, None)

    if not service:
        return '/'

    service_instance = service()
    return service_instance.get_auth_url()
