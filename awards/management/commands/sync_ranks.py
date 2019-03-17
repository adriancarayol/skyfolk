from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from awards.award_recipes import award_register
from awards.models import UserRank
from loguru import logger


class Command(BaseCommand):
    help = 'Sync UserRank with DB'

    def handle(self, *args, **options):
        user_ranks = [UserRank(name=award.name, description=award.description, reached_with=award.reached_with) 
                      for award in award_register.awards_recipes]
        try:
            UserRank.objects.bulk_create(user_ranks)
        except IntegrityError:
            for user_rank in user_ranks:
                try:
                    user_rank.save()
                except IntegrityError:
                    continue
        
        logger.info('{} sync to DB'.format(user_ranks))
