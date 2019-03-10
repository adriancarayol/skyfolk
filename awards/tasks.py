from django.db.models import Sum
from django.contrib.auth.models import User
from awards.models import UserRank
from badgify.models import Badge
from skyfolk.celery import app
from loguru import logger


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
