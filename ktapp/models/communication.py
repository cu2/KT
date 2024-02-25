from django.db import models
from django.core.urlresolvers import reverse
from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver


class Banner(models.Model):
    published_at = models.DateTimeField(auto_now_add=True)
    where = models.CharField(max_length=32)
    what = models.CharField(max_length=32)
    user = models.ForeignKey('KTUser', blank=True, null=True, on_delete=models.SET_NULL)
    BANNER_STATUS_PUBLISHED = 'P'
    BANNER_STATUS_VIEWED = 'V'
    BANNER_STATUS_CLOSED = 'C'
    BANNER_STATUS_WITHDRAWN = 'W'
    BANNER_STATUSES = [
        (BANNER_STATUS_PUBLISHED, 'Published'),
        (BANNER_STATUS_VIEWED, 'Viewed'),
        (BANNER_STATUS_CLOSED, 'Closed'),
        (BANNER_STATUS_WITHDRAWN, 'Withdrawn'),
    ]
    status = models.CharField(max_length=1, choices=BANNER_STATUSES, default=BANNER_STATUS_PUBLISHED)
    first_viewed_at = models.DateTimeField(blank=True, null=True)
    viewed = models.PositiveSmallIntegerField(default=0)
    closed_at = models.DateTimeField(blank=True, null=True)
    withdrawn_at = models.DateTimeField(blank=True, null=True)


class EmailCampaign(models.Model):
    title = models.CharField(max_length=250)
    recipients = models.CharField(max_length=250, blank=True, null=True)
    subject = models.CharField(max_length=250)
    html_message = models.TextField(blank=True)
    text_message = models.TextField(blank=True)
    pm_message = models.TextField(blank=True)
    sent_at = models.DateField()

    def __unicode__(self):
        return '{} @ {}'.format(self.title, self.sent_at)


class EmailSend(models.Model):
    user = models.ForeignKey('KTUser', blank=True, null=True, on_delete=models.SET_NULL)
    email_type = models.CharField(max_length=250, blank=True, null=True)
    campaign = models.ForeignKey(EmailCampaign, blank=True, null=True, on_delete=models.SET_NULL)
    email = models.CharField(max_length=250)
    sent_at = models.DateTimeField(auto_now_add=True)
    is_pm = models.BooleanField(default=False)
    is_email = models.BooleanField(default=False)
    is_success = models.BooleanField(default=False)


class EmailBounce(models.Model):
    email = models.CharField(max_length=250)
    bounced_at = models.DateField()


class EmailOpen(models.Model):
    user = models.ForeignKey('KTUser', blank=True, null=True, on_delete=models.SET_NULL)
    email_type = models.CharField(max_length=250, blank=True, null=True)
    campaign = models.ForeignKey(EmailCampaign, blank=True, null=True, on_delete=models.SET_NULL)
    opened_at = models.DateTimeField(auto_now_add=True)


class EmailClick(models.Model):
    user = models.ForeignKey('KTUser', blank=True, null=True, on_delete=models.SET_NULL)
    email_type = models.CharField(max_length=250, blank=True, null=True)
    campaign = models.ForeignKey(EmailCampaign, blank=True, null=True, on_delete=models.SET_NULL)
    clicked_at = models.DateTimeField(auto_now_add=True)
    url = models.CharField(max_length=250)


class EmailUnsubscribe(models.Model):
    user = models.ForeignKey('KTUser', blank=True, null=True, on_delete=models.SET_NULL)
    email_type = models.CharField(max_length=250, blank=True, null=True)
    campaign = models.ForeignKey(EmailCampaign, blank=True, null=True, on_delete=models.SET_NULL)
    unsubscribed_at = models.DateTimeField(auto_now_add=True)


class Notification(models.Model):
    target_user = models.ForeignKey('KTUser', related_name='noti_target_user')
    created_at = models.DateTimeField(auto_now_add=True)
    NOTIFICATION_TYPE_COMMENT = 'Co'
    NOTIFICATION_TYPES = [
        (NOTIFICATION_TYPE_COMMENT, 'Comment'),
    ]
    notification_type = models.CharField(max_length=2, choices=NOTIFICATION_TYPES, default=NOTIFICATION_TYPE_COMMENT)
    NOTIFICATION_SUBTYPE_COMMENT_REPLY = 'CoRe'
    NOTIFICATION_SUBTYPE_COMMENT_MENTION = 'CoMe'
    NOTIFICATION_SUBTYPE_COMMENT_ON_FILM_YOU_SUBSCRIBED_TO = 'CoFS'
    NOTIFICATION_SUBTYPE_COMMENT_ON_TOPIC_YOU_SUBSCRIBED_TO = 'CoTS'
    NOTIFICATION_SUBTYPE_COMMENT_ON_POLL_YOU_SUBSCRIBED_TO = 'CoPS'
    NOTIFICATION_SUBTYPES = [
        (NOTIFICATION_SUBTYPE_COMMENT_REPLY, 'Comment reply'),
        (NOTIFICATION_SUBTYPE_COMMENT_MENTION, 'Comment mention'),
        (NOTIFICATION_SUBTYPE_COMMENT_ON_FILM_YOU_SUBSCRIBED_TO, 'Comment on film you subscribed to'),
        (NOTIFICATION_SUBTYPE_COMMENT_ON_TOPIC_YOU_SUBSCRIBED_TO, 'Comment on topic you subscribed to'),
        (NOTIFICATION_SUBTYPE_COMMENT_ON_POLL_YOU_SUBSCRIBED_TO, 'Comment on poll you subscribed to'),
    ]
    notification_subtype = models.CharField(max_length=4, choices=NOTIFICATION_SUBTYPES, blank=True)
    film = models.ForeignKey('Film', blank=True, null=True, on_delete=models.SET_NULL)
    topic = models.ForeignKey('Topic', blank=True, null=True, on_delete=models.SET_NULL)
    poll = models.ForeignKey('Poll', blank=True, null=True, on_delete=models.SET_NULL)
    source_user = models.ForeignKey('KTUser', blank=True, null=True, on_delete=models.SET_NULL, related_name='noti_source_user')
    is_read = models.BooleanField(default=False)
    comment = models.ForeignKey('Comment', blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        index_together = [
            ['target_user', 'created_at'],
        ]

    def save(self, *args, **kwargs):
        super(Notification, self).save(*args, **kwargs)
        self.target_user.unread_notification_count = Notification.objects.filter(target_user=self.target_user, is_read=False).count()
        self.target_user.save(update_fields=['unread_notification_count'])

    @property
    def url(self):
        if self.notification_type == 'Co':
            if self.film:
                return reverse('film_comments', args=(self.film.id, self.film.slug_cache))
            if self.topic:
                return reverse('forum', args=(self.topic.id, self.topic.slug_cache))
            if self.poll:
                return reverse('poll', args=(self.poll.id, self.poll.slug_cache))
        return None


@receiver(post_delete, sender=Notification)
def delete_notification(sender, instance, **kwargs):
    instance.target_user.unread_notification_count = Notification.objects.filter(target_user=instance.target_user, is_read=False).count()
    instance.target_user.save(update_fields=['unread_notification_count'])
