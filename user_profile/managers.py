from django.db import models
from django.db.models import Count, Sum, Subquery, OuterRef

from badgify.models import Award
from user_profile.constants import FOLLOWING, BLOCK


class ProfileManager(models.Manager):
    def build_sky_id(self, profile):
        """
        Returns all information of profile given a user profile
        Information contains:
            Stats like multimedia, followers and likes
            Range and Exp
            Interests
        :param profile:
        :return: Queryset with all information
        """
        pass


class RelationShipProfileManager(models.Manager):
    def get_total_following(self, profile_id):
        """
        Return total following of profile_id
        :param profile_id: Profile
        :return: Total following
        """
        qs = self.get_queryset()
        return qs.filter(from_profile=profile_id, type=FOLLOWING).count()

    def get_total_followers(self, profile_id):
        """
        Return total followers of profile_id
        :param profile_id: Profile
        :return: Total followers
        """
        qs = self.get_queryset()
        return qs.filter(to_profile=profile_id, type=FOLLOWING).count()

    def is_follow(self, to_profile, from_profile):
        """
        Return if from_profile follow to_profile
        :param to_profile:
        :param from_profile:
        :return:
        """
        qs = self.get_queryset()
        return qs.filter(to_profile=to_profile, from_profile=from_profile, type=FOLLOWING).exists()

    def is_blocked(self, to_profile, from_profile):
        """
        Return if from_profile blocks to_profile
        :param to_profile:
        :param from_profile:
        :return:
        """
        qs = self.get_queryset()
        return qs.filter(to_profile=to_profile, from_profile=from_profile, type=BLOCK).exists()

    def get_sky_id_from_my_following(self, from_profile) -> models.QuerySet:
        """
        Returns all information of profile given a profile
        Information contains:
            Stats like multimedia, followers and likes
            Range and Exp
            Interests
        :param from_profile:
        :return: Queryset with all information
        """
        last_badge = Award.objects.filter(user_id=OuterRef('to_profile__user')).order_by('-awarded_at')

        return (
            self.filter(
                from_profile=from_profile, type=FOLLOWING
            ).prefetch_related("to_profile__tags", "to_profile__to_like", "to_profile__relationships__to_profile")
             .select_related('to_profile__user')
             .annotate(followers=Count("to_profile__to_profile"))
             .annotate(photos=Count("to_profile__user__user_photos"))
             .annotate(videos=Count("to_profile__user__user_videos"))
             .annotate(experience=Sum("to_profile__user__badges__badge__points"))
             .annotate(last_award=Subquery(last_badge.values('badge__category')[:1]))
        )
