from django.db.models.signals import post_save
from django.dispatch import receiver
from badgify.models import Award, Badge
from .models import Photo, Video


@receiver(post_save, sender=Photo)
@receiver(post_save, sender=Video)
def handle_new_relationship(sender, instance, created, **kwargs):
    photo_count = Photo.objects.filter(owner=instance.owner).count()
    video_count = Video.objects.filter(owner=instance.owner).count()

    total_count = photo_count + video_count

    if total_count >= 1:
        Award.objects.get_or_create(
            user=instance.owner, badge=Badge.objects.get(slug="first-upload-media")
        )
