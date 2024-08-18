from django.conf import settings
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver


class Vote(models.Model):
    film = models.ForeignKey('Film')
    user = models.ForeignKey('KTUser')
    rating = models.PositiveSmallIntegerField()
    when = models.DateTimeField(auto_now_add=True, null=True)
    shared_on_facebook = models.BooleanField(default=False)

    def __unicode__(self):
        return self.film.orig_title + ' + ' + self.user.username + ' = ' + unicode(self.rating)

    class Meta:
        unique_together = ['film', 'user']

    def save(self, *args, **kwargs):
        from .recommendation import Recommendation
        from ..utils import get_app_config
        vapiti_year = get_app_config('vapiti_year')
        super(Vote, self).save(*args, **kwargs)
        self.film.comment_set.filter(created_by=self.user).update(rating=self.rating)
        Wishlist.objects.filter(film=self.film, wished_by=self.user, wish_type=Wishlist.WISH_TYPE_YES).delete()
        self.user.latest_votes = ','.join([unicode(v.id) for v in self.user.vote_set.all().order_by('-when', '-id')[:100]])
        self.user.number_of_ratings = self.user.vote_set.count()
        self.user.number_of_ratings_1 = self.user.vote_set.filter(rating=1).count()
        self.user.number_of_ratings_2 = self.user.vote_set.filter(rating=2).count()
        self.user.number_of_ratings_3 = self.user.vote_set.filter(rating=3).count()
        self.user.number_of_ratings_4 = self.user.vote_set.filter(rating=4).count()
        self.user.number_of_ratings_5 = self.user.vote_set.filter(rating=5).count()
        self.user.number_of_vapiti_votes = self.user.vote_set.filter(film__vapiti_year=vapiti_year).count()
        self.user.vapiti_weight = self.user.number_of_ratings + 25 * self.user.number_of_vapiti_votes
        if self.user.number_of_ratings < 10:
            self.user.average_rating = None
        else:
            self.user.average_rating = 1.0 * (
                1*self.user.number_of_ratings_1+
                2*self.user.number_of_ratings_2+
                3*self.user.number_of_ratings_3+
                4*self.user.number_of_ratings_4+
                5*self.user.number_of_ratings_5
            ) / self.user.number_of_ratings
        self.user.save(update_fields=[
            'latest_votes', 'number_of_ratings',
            'number_of_ratings_1', 'number_of_ratings_2', 'number_of_ratings_3', 'number_of_ratings_4', 'number_of_ratings_5',
            'average_rating', 'number_of_vapiti_votes', 'vapiti_weight',
        ])
        Recommendation.recalculate_fav_for_users_and_film(self.user.get_followed_by(), self.film)


@receiver(post_delete, sender=Vote)
def delete_vote(sender, instance, **kwargs):
    from .content import Film
    from .recommendation import Recommendation
    from ..utils import get_app_config
    vapiti_year = get_app_config('vapiti_year')
    try:
        instance.film.comment_set.filter(created_by=instance.user).update(rating=None)
    except Film.DoesNotExist:
        pass
    instance.user.latest_votes = ','.join([unicode(v.id) for v in instance.user.vote_set.all().order_by('-when', '-id')[:100]])
    instance.user.number_of_ratings = instance.user.vote_set.count()
    instance.user.number_of_ratings_1 = instance.user.vote_set.filter(rating=1).count()
    instance.user.number_of_ratings_2 = instance.user.vote_set.filter(rating=2).count()
    instance.user.number_of_ratings_3 = instance.user.vote_set.filter(rating=3).count()
    instance.user.number_of_ratings_4 = instance.user.vote_set.filter(rating=4).count()
    instance.user.number_of_ratings_5 = instance.user.vote_set.filter(rating=5).count()
    instance.user.number_of_vapiti_votes = instance.user.vote_set.filter(film__vapiti_year=vapiti_year).count()
    instance.user.vapiti_weight = instance.user.number_of_ratings + 25 * instance.user.number_of_vapiti_votes
    if instance.user.number_of_ratings < 10:
        instance.user.average_rating = None
    else:
        instance.user.average_rating = 1.0 * (
            1*instance.user.number_of_ratings_1+
            2*instance.user.number_of_ratings_2+
            3*instance.user.number_of_ratings_3+
            4*instance.user.number_of_ratings_4+
            5*instance.user.number_of_ratings_5
        ) / instance.user.number_of_ratings
    instance.user.save(update_fields=[
        'latest_votes', 'number_of_ratings',
        'number_of_ratings_1', 'number_of_ratings_2', 'number_of_ratings_3', 'number_of_ratings_4', 'number_of_ratings_5',
        'average_rating', 'number_of_vapiti_votes', 'vapiti_weight',
    ])
    Recommendation.recalculate_fav_for_users_and_film(instance.user.get_followed_by(), instance.film)


class Follow(models.Model):
    who = models.ForeignKey('KTUser', related_name='follows')
    whom = models.ForeignKey('KTUser', related_name='followed_by')
    started_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        from .recommendation import Recommendation
        super(Follow, self).save(*args, **kwargs)
        Recommendation.recalculate_fav_for_user_and_user(self.who, self.whom)


@receiver(post_delete, sender=Follow)
def delete_follow(sender, instance, **kwargs):
    from .recommendation import Recommendation
    Recommendation.recalculate_fav_for_user_and_user(instance.who, instance.whom)


class Subscription(models.Model):
    SUBSCRIPTION_TYPE_SUBSCRIBE = 'S'
    SUBSCRIPTION_TYPE_IGNORE = 'I'
    SUBSCRIPTION_TYPES = [
        (SUBSCRIPTION_TYPE_SUBSCRIBE, 'Subscribe'),
        (SUBSCRIPTION_TYPE_IGNORE, 'Ignore'),
    ]

    user = models.ForeignKey('KTUser')
    subscribed_at = models.DateTimeField(auto_now_add=True)
    subscription_type = models.CharField(max_length=1, choices=SUBSCRIPTION_TYPES, default=SUBSCRIPTION_TYPE_SUBSCRIBE)
    film = models.ForeignKey('Film', blank=True, null=True, on_delete=models.SET_NULL)
    topic = models.ForeignKey('Topic', blank=True, null=True, on_delete=models.SET_NULL)
    poll = models.ForeignKey('Poll', blank=True, null=True, on_delete=models.SET_NULL)

    @classmethod
    def get_subscription_status(cls, user, film=None, topic=None, poll=None):
        qs = cls.objects.filter(user=user)
        if film:
            qs = qs.filter(film=film)
        if topic:
            qs = qs.filter(topic=topic)
        if poll:
            qs = qs.filter(poll=poll)
        try:
            sub = qs[0]
        except IndexError:
            return ''
        return sub.subscription_type

    @classmethod
    def subscribe(cls, action, user, film=None, topic=None, poll=None):
        your_subscription = cls.get_subscription_status(
            user=user,
            film=film,
            topic=topic,
            poll=poll,
        )
        sub_data = {
            'user': user,
            'film': film,
            'topic': topic,
            'poll': poll,
        }
        if your_subscription == '':
            if action == 'sub':
                cls.objects.create(
                    subscription_type=cls.SUBSCRIPTION_TYPE_SUBSCRIBE,
                    **sub_data
                )
            elif action == 'ignore':
                cls.objects.create(
                    subscription_type=cls.SUBSCRIPTION_TYPE_IGNORE,
                    **sub_data
                )
        elif your_subscription == 'S':
            if action in {'unsub', 'ignore'}:
                cls.objects.filter(**sub_data).delete()
            if action == 'ignore':
                cls.objects.create(
                    subscription_type=cls.SUBSCRIPTION_TYPE_IGNORE,
                    **sub_data
                )
        elif your_subscription == 'I':
            if action in {'unignore', 'sub'}:
                cls.objects.filter(**sub_data).delete()
            if action == 'sub':
                cls.objects.create(
                    subscription_type=cls.SUBSCRIPTION_TYPE_SUBSCRIBE,
                    **sub_data
                )


class Wishlist(models.Model):
    film = models.ForeignKey('Film')
    wished_by = models.ForeignKey('KTUser')
    wished_at = models.DateTimeField(auto_now_add=True)
    WISH_TYPE_YES = 'Y'
    WISH_TYPE_NO = 'N'
    WISH_TYPE_GET = 'G'
    WISH_TYPES = [
        (WISH_TYPE_YES, 'Yes'),
        (WISH_TYPE_NO, 'No'),
        (WISH_TYPE_GET, 'Get'),
    ]
    wish_type = models.CharField(max_length=1, choices=WISH_TYPES, default=WISH_TYPE_YES)

    class Meta:
        unique_together = ['film', 'wished_by', 'wish_type']


    def save(self, *args, **kwargs):
        super(Wishlist, self).save(*args, **kwargs)
        if self.wish_type == Wishlist.WISH_TYPE_YES:
            self.wished_by.number_of_wishes_yes = Wishlist.objects.filter(wished_by=self.wished_by, wish_type=Wishlist.WISH_TYPE_YES).count()
            self.wished_by.save(update_fields=['number_of_wishes_yes'])
        elif self.wish_type == Wishlist.WISH_TYPE_NO:
            self.wished_by.number_of_wishes_no = Wishlist.objects.filter(wished_by=self.wished_by, wish_type=Wishlist.WISH_TYPE_NO).count()
            self.wished_by.save(update_fields=['number_of_wishes_no'])
        else:
            self.wished_by.number_of_wishes_get = Wishlist.objects.filter(wished_by=self.wished_by, wish_type=Wishlist.WISH_TYPE_GET).count()
            self.wished_by.save(update_fields=['number_of_wishes_get'])


@receiver(post_delete, sender=Wishlist)
def delete_wish(sender, instance, **kwargs):
    if instance.wish_type == Wishlist.WISH_TYPE_YES:
        instance.wished_by.number_of_wishes_yes = Wishlist.objects.filter(wished_by=instance.wished_by, wish_type=Wishlist.WISH_TYPE_YES).count()
        instance.wished_by.save(update_fields=['number_of_wishes_yes'])
    elif instance.wish_type == Wishlist.WISH_TYPE_NO:
        instance.wished_by.number_of_wishes_no = Wishlist.objects.filter(wished_by=instance.wished_by, wish_type=Wishlist.WISH_TYPE_NO).count()
        instance.wished_by.save(update_fields=['number_of_wishes_no'])
    else:
        instance.wished_by.number_of_wishes_get = Wishlist.objects.filter(wished_by=instance.wished_by, wish_type=Wishlist.WISH_TYPE_GET).count()
        instance.wished_by.save(update_fields=['number_of_wishes_get'])


class IgnoreUser(models.Model):
    who = models.ForeignKey('KTUser', related_name='+', on_delete=models.CASCADE)
    whom = models.ForeignKey('KTUser', related_name='+', on_delete=models.CASCADE)
    when = models.DateTimeField(auto_now_add=True)
    ignore_pm = models.BooleanField(default=False)
    ignore_comment = models.BooleanField(default=False)

    class Meta:
        unique_together = ['who', 'whom']

    @classmethod
    def get(cls, who, whom):
        try:
            ignore_user = cls.objects.get(who=who, whom=whom)
        except cls.DoesNotExist:
            return False, False
        return ignore_user.ignore_pm, ignore_user.ignore_comment

    @classmethod
    def set(cls, who, whom, ignore_pm=None, ignore_comment=None):
        if ignore_pm is None or ignore_comment is None:
            old_ignore_pm, old_ignore_comment = cls.get(who=who, whom=whom)
            if ignore_pm is None:
                ignore_pm = old_ignore_pm
            if ignore_comment is None:
                ignore_comment = old_ignore_comment
        if not ignore_pm and not ignore_comment:
            cls.objects.filter(who=who, whom=whom).delete()
            return
        cls.objects.update_or_create(
            who=who,
            whom=whom,
            defaults={
                'ignore_pm': ignore_pm,
                'ignore_comment': ignore_comment,
            }
        )


class SuggestedContent(models.Model):
    created_by = models.ForeignKey('KTUser', blank=True, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    DOMAIN_FILM = 'F'
    DOMAIN_LINK = 'L'
    DOMAINS = [
        (DOMAIN_FILM, 'Film'),
        (DOMAIN_LINK, 'Link'),
    ]
    domain = models.CharField(max_length=1, choices=DOMAINS, default=DOMAIN_FILM)
    content = models.TextField(blank=True)
