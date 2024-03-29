import datetime
import math
import random

from django.core.management.base import BaseCommand
from django.db.models import Q

from ktapp import models
from ktapp import utils as kt_utils


class Command(BaseCommand):
    help = 'Publish banners'

    def handle(self, *args, **options):
        self.publish_fundraiser_banners()

    def publish_fundraiser_banners(self):
        a_week_ago = datetime.date.today() - datetime.timedelta(days=7)
        a_month_ago = datetime.date.today() - datetime.timedelta(days=30)
        a_year_ago = datetime.date.today() - datetime.timedelta(days=365)
        user_ids = set([user['id'] for user in models.KTUser.objects.filter(
            is_active=True,
            core_member=True,
            last_activity_at__gt=a_week_ago,
        ).values('id')])
        banner_user_ids = set(banner['user_id'] for banner in models.Banner.objects.filter(
            Q(published_at__gt=a_month_ago)
            | Q(closed_at__gt=a_month_ago)
        ).exclude(user_id=None).values('user_id'))
        donation_user_ids = set(donation['given_by_id'] for donation in models.Donation.objects.filter(
            given_at__gt=a_year_ago
        ).exclude(given_by_id=None).values('given_by_id'))
        target_population = user_ids - banner_user_ids - donation_user_ids

        current_finance = kt_utils.get_current_finance()
        if current_finance is None:
            self.stdout.write('Skip publishing fundraiser banner.')
            return
        current_balance = current_finance['opening_balance'] + current_finance['donations']
        plan_fulfillment = math.floor(100.0 * current_balance / current_finance['planned_cost'])
        if plan_fulfillment < 0:
            plan_fulfillment = 0
        if plan_fulfillment > 100:
            plan_fulfillment = 100

        how_many_users = int(34 - plan_fulfillment / 3.0)  # 0..34
        if how_many_users > len(target_population):
            how_many_users = len(target_population)
        if how_many_users == 0:
            self.stdout.write('Skip publishing fundraiser banner.')
            return

        self.stdout.write('Publishing fundraiser banner for %d users... (out of %d)' % (how_many_users, len(target_population)))
        for user_id in random.sample(target_population, how_many_users):
            self.stdout.write('%d' % user_id)
            models.Banner.objects.create(
                where='index',
                what='fundraiser',
                user_id=user_id,
            )
        self.stdout.write('Published fundraiser banner for %d users.' % how_many_users)
