import datetime

from django.core.management.base import BaseCommand

from ktapp import models
from ktapp import utils as kt_utils


class Command(BaseCommand):
    help = 'Check temporarily banned users'

    def handle(self, *args, **options):
        self.stdout.write('Checking temporarily banned users...')
        for u in models.KTUser.objects.filter(is_active=False, reason_of_inactivity=models.KTUser.REASON_TEMPORARILY_BANNED, banned_until__lte=datetime.datetime.now()):
            state_before = {
                'is_active': u.is_active,
                'reason': u.reason_of_inactivity,
                'banned_until': u.banned_until,
            }
            u.is_active = True
            u.reason_of_inactivity = models.KTUser.REASON_UNKNOWN
            u.banned_until = None
            u.save()
            kt_utils.changelog(
                models.Change,
                None,
                'end_of_temp_ban',
                'user:%s' % u.id,
                state_before, {
                    'is_active': u.is_active,
                    'reason': u.reason_of_inactivity,
                    'banned_until': u.banned_until,
                },
            )
            self.stdout.write(u'User[%d] %s is back' % (u.id, u.username))
        self.stdout.write('Checked temporarily banned users.')
