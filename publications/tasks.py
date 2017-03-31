from celery.schedules import crontab
from celery.task import periodic_task
from .models import Publication, PublicationDeleted
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@periodic_task(run_every=crontab(hour=4, minute=30, day_of_week=1))
def clean_deleted_publications():
    publications = Publication.objects.filter(deleted=True)
    for publication in publications:
        pub, created = PublicationDeleted.objects.get_or_create(author=publication.author, content=publication.content,
                                          image=publication.image, created=publication.created)
        publication.delete()
        logger.info("Publication safe deleted {}".format(pub.id))