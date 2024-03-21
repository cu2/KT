from __future__ import unicode_literals

import datetime

from django.conf import settings
from django.core.management.base import BaseCommand

from ktapp import models
from ktapp import utils as kt_utils


class Command(BaseCommand):
    help = "Publish Vapiti stats"

    def handle(self, *args, **options):
        self.stdout.write("Publishing Vapiti stats...")
        (
            vapiti_round,
            round_1_dates,
            round_2_dates,
            result_day,
        ) = kt_utils.get_vapiti_round()
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        if today_str == round_2_dates[0]:
            self.publish_stats(1)
        if today_str == result_day:
            self.publish_stats(2)
        self.stdout.write("Published Vapiti stats.")

    def publish_stats(self, vapiti_round):
        self.stdout.write(
            "Publishing Vapiti stats for round {}...".format(vapiti_round)
        )
        stats = kt_utils.get_vapiti_stats(vapiti_round)
        for vapiti_type, stat in stats.items():
            for key, value in stat.items():
                models.VapitiStat.objects.update_or_create(
                    year=settings.VAPITI_YEAR,
                    vapiti_round=vapiti_round,
                    vapiti_type=vapiti_type,
                    defaults={key: value},
                )
        self.stdout.write("Published.")
