import datetime

from django.core.management.base import BaseCommand

from ktapp import models


class Command(BaseCommand):
    help = 'Delete old notifications'

    def handle(self, *args, **options):
        self.stdout.write('Deleting old notifications...')
        three_month_ago = datetime.datetime.now() - datetime.timedelta(days=91)
        delete_count, _ = models.Notification.objects.filter(created_at__lte=three_month_ago).delete()
        self.stdout.write('Deleted %s old notifications.' % delete_count)
