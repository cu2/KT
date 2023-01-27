from django.core.management.base import BaseCommand

from ktapp import models


class Command(BaseCommand):
    help = "Merge users"

    def add_arguments(self, parser):
        parser.add_argument("source_user_id", type=int)
        parser.add_argument("target_user_id", type=int)

    def handle(self, *args, **options):
        self.source_user = models.KTUser.objects.get(id=options["source_user_id"])
        self.target_user = models.KTUser.objects.get(id=options["target_user_id"])
        self.stdout.write(
            "Merging user {} into user {}...".format(self.source_user, self.target_user)
        )
        self.move_votes()
        self.move_comments()
        self.stdout.write("User merged.")

    def move_votes(self):
        # if there was no vote, we create a new
        # if there was already, we don't touch it
        for vote in models.Vote.objects.filter(user=self.source_user).order_by("id"):
            self.stdout.write(
                "Moving vote {} for film {}...".format(vote.rating, vote.film)
            )
            models.Vote.objects.get_or_create(
                film=vote.film,
                user=self.target_user,
                defaults={"rating": vote.rating, "shared_on_facebook": False},
            )
            vote.delete()

    def move_comments(self):
        for comment in models.Comment.objects.filter(
            created_by=self.source_user
        ).order_by("id"):
            self.stdout.write(
                "Moving comment {} at {} on {} {}...".format(
                    comment.id,
                    comment.created_at,
                    comment.domain,
                    comment.domain_object,
                )
            )
            comment.created_by = self.target_user
            if comment.domain == models.Comment.DOMAIN_FILM:
                try:
                    vote = models.Vote.objects.get(
                        film=comment.film, user=self.target_user
                    )
                    comment.rating = vote.rating
                except models.Vote.DoesNotExist:
                    comment.rating = None
            comment.save()
        self.fix_comment_metadata(self.target_user)
        self.fix_comment_metadata(self.source_user)

    def fix_comment_metadata(self, user):
        self.stdout.write("Fixing comment metadata for user {}...".format(user))
        user.latest_comments = ",".join(
            [
                unicode(comment.id)
                for comment in user.comment_set.all().order_by("-created_at", "-id")[
                    :100
                ]
            ]
        )
        user.number_of_comments = user.comment_set.count()
        user.number_of_film_comments = user.comment_set.filter(
            domain=models.Comment.DOMAIN_FILM
        ).count()
        user.number_of_topic_comments = user.comment_set.filter(
            domain=models.Comment.DOMAIN_TOPIC
        ).count()
        user.number_of_poll_comments = user.comment_set.filter(
            domain=models.Comment.DOMAIN_POLL
        ).count()
        user.save(
            update_fields=[
                "latest_comments",
                "number_of_comments",
                "number_of_film_comments",
                "number_of_topic_comments",
                "number_of_poll_comments",
            ]
        )
        for idx, comment in enumerate(
            models.Comment.objects.filter(created_by=user).order_by("created_at", "id")
        ):
            comment.serial_number_by_user = idx + 1
            comment.save()
