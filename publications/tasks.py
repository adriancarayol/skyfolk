import os
from .models import Publication, PublicationDeleted
from celery.utils.log import get_task_logger
from skyfolk.celery import app

logger = get_task_logger(__name__)


@app.task(name='tasks.clean_deleted_publications')
def clean_deleted_publications():
    logger.info('Finding deleted publications...')
    publications = Publication.objects.filter(deleted=True)
    for publication in publications:
        pub, created = PublicationDeleted.objects.get_or_create(author=publication.author, content=publication.content,
                                                                created=publication.created)
        extra_content = publication.extra_content
        shared = publication.shared_publication
        if extra_content:
            extra_content.delete()
        if shared:
            shared.publication.shared -= 1
            shared.publication.save()
            shared.delete()

        logger.info('Deleting images...')
        for img in publication.images.all():
            if img.image:
                if os.path.isfile(img.image.path):
                    os.remove(img.image.path)
            img.delete()
            logger.info('Image deleted')
        publication.delete()
        logger.info("Publication safe deleted {}".format(pub.id))