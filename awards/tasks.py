import gc
from django.db.models import Sum
from django.contrib.auth.models import User
from awards.models import UserRank
from badgify.models import Badge
from skyfolk.celery import app
from loguru import logger


def queryset_iterator(queryset, chunksize=1000):
    '''''
    Iterate over a Django Queryset ordered by the primary key

    This method loads a maximum of chunksize (default: 1000) rows in it's
    memory at the same time while django normally would load all rows in it's
    memory. Using the iterator() method only causes it to not preload all the
    classes.

    Note that the implementation of the iterator does not support ordered query sets.
    '''
    pk = 0
    last_pk = queryset.order_by('-pk')[0].pk
    queryset = queryset.order_by('pk')
    while pk < last_pk:
        for row in queryset.filter(pk__gt=pk)[:chunksize]:
            pk = row.pk
            yield row
        gc.collect()


@app.task(name="tasks.check_rank_on_new_award")
def check_rank_on_new_award(user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return False

    total_points = Badge.objects.filter(users__id=user_id).aggregate(total_points=Sum('points'))['total_points'] or 0
    user_ranks = UserRank.objects.filter(reached_with__lte=total_points).exclude(users__id=user_id)

    logger.info('Puntos: {}'.format(total_points))
    logger.info('Not in user ranks: {}'.format(user_ranks))

    for user_rank in user_ranks:
        logger.info("Rank {} added to user {}".format(user_rank, user))
        user_rank.users.add(user)

    return True


@app.task(name="tasks.periodic_checking_ranks")
def periodic_checking_ranks():
    for user in queryset_iterator(User.objects.all()):
        total_points = Badge.objects.filter(users__id=user.id).aggregate(total_points=Sum('points'))['total_points'] or 0
        user_ranks = UserRank.objects.filter(reached_with__lte=total_points).exclude(users__id=user.id)
        for user_rank in user_ranks:
            logger.info('Rank {} added to user: {}'.format(user_rank, user))
            user_rank.users.add(user)
