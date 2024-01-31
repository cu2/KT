from django.core.management.base import BaseCommand

from ktapp import models


TEST_USER_IDS = [1]


PM_TEMPLATE = u"""Kedves {username}!

{text_message}


a szerk
"""


class Command(BaseCommand):
    help = "Send email campaign"
    # Note: actual email was phased out for campaigns, we are using PMs instead.

    def add_arguments(self, parser):
        parser.add_argument("campaign_id", type=int)
        parser.add_argument("target", choices=["test", "core", "everybody"])

    def handle(self, *args, **options):
        campaign_id = options["campaign_id"]
        self.target = options["target"]
        self.campaign = models.EmailCampaign.objects.get(id=campaign_id)
        self.stdout.write(
            'Sending email campaign title="{title}" ID={id} to {target}...'.format(
                title=self.campaign.title, id=self.campaign.id, target=self.target
            )
        )
        target_users = self._get_target_users()
        for user in target_users:
            self._reach_user(user)
        self.stdout.write("Email campaign sent.")

    def _get_target_users(self):
        users = models.KTUser.objects
        filtered_users = {
            "test": users.filter(id__in=TEST_USER_IDS),
            "core": users.filter(is_active=True, core_member=True),
            "everybody": users.filter(is_active=True),
        }[self.target]
        return filtered_users.order_by("id")

    def _reach_user(self, user):
        self.stdout.write("[{id}] {name}".format(id=user.id, name=user.username))
        models.Message.send_message(
            sent_by=None,
            content=PM_TEMPLATE.format(
                username=user.username,
                text_message=self.campaign.pm_message,
            ),
            recipients=[user],
        )
