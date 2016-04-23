import datetime

from django.core.management.base import BaseCommand

from ktapp import models


class Command(BaseCommand):
    help = 'Check temporarily banned users'

    def handle(self, *args, **options):
        self.stdout.write('Checking temporarily banned users...')
        for u in models.KTUser.objects.filter(is_active=False, reason_of_inactivity=models.KTUser.REASON_TEMPORARILY_BANNED, banned_until__lte=datetime.datetime.now()):
            u.is_active = True
            u.reason_of_inactivity = models.KTUser.REASON_UNKNOWN
            u.banned_until = None
            u.save()
            self.stdout.write(u'User[%d] %s is back' % (u.id, u.username))
        self.stdout.write('Checked temporarily banned users.')
