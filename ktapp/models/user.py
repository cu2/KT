from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.core.mail import EmailMultiAlternatives
from django.template.defaultfilters import slugify
from django.utils.crypto import get_random_string
from django.utils.html import strip_tags

from ktapp import utils as kt_utils
from ktapp import texts


class KTUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=64, unique=True)
    email = models.EmailField(blank=True, unique=True)
    future_email = models.EmailField(blank=True)

    is_staff = models.BooleanField(default=False)
    is_editor = models.BooleanField(default=False)
    is_ex_editor = models.BooleanField(default=False)
    is_moderator = models.BooleanField(default=False)
    is_ex_moderator = models.BooleanField(default=False)
    is_reliable = models.BooleanField(default=False)
    is_game_master = models.BooleanField(default=False)
    core_member = models.BooleanField(default=False)

    @property
    def is_at_least_reliable(self):
        return self.is_editor or self.is_ex_editor or self.is_reliable

    is_active = models.BooleanField(default=True)  # delete
    date_joined = models.DateTimeField(auto_now_add=True)
    GENDER_TYPE_MALE = 'M'
    GENDER_TYPE_FEMALE = 'F'
    GENDER_TYPE_UNKNOWN = 'U'
    GENDER_TYPES = [
        (GENDER_TYPE_MALE, 'Male'),
        (GENDER_TYPE_FEMALE, 'Female'),
        (GENDER_TYPE_UNKNOWN, 'Unknown'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_TYPES, default=GENDER_TYPE_UNKNOWN)
    location = models.CharField(max_length=250, blank=True, null=True)
    year_of_birth = models.PositiveIntegerField(default=0)
    public_gender = models.BooleanField(default=True)
    public_location = models.BooleanField(default=True)
    public_year_of_birth = models.BooleanField(default=True)
    follow = models.ManyToManyField('KTUser', symmetrical=False, through='Follow', through_fields=('who', 'whom'))
    slug_cache = models.CharField(max_length=250, blank=True)
    validated_email = models.BooleanField(default=False)
    validated_email_at = models.DateTimeField(blank=True, null=True)
    i_county_id = models.SmallIntegerField(default=-1)
    email_notification = models.BooleanField(default=False)
    facebook_rating_share = models.BooleanField(default=True)
    added_role = models.PositiveIntegerField(default=0)
    added_artist = models.PositiveIntegerField(default=0)
    added_film = models.PositiveIntegerField(default=0)
    added_trivia = models.PositiveIntegerField(default=0)
    REASON_BANNED = 'B'
    REASON_TEMPORARILY_BANNED = 'T'
    REASON_QUIT = 'Q'
    REASON_UNKNOWN = 'U'
    REASONS = [
        (REASON_BANNED, 'Banned'),
        (REASON_TEMPORARILY_BANNED, 'Temporarily Banned'),
        (REASON_QUIT, 'Quit'),
        (REASON_UNKNOWN, 'Unknown'),
    ]
    reason_of_inactivity = models.CharField(max_length=1, choices=REASONS, default=REASON_UNKNOWN)
    banned_until = models.DateTimeField(blank=True, null=True)
    old_permissions = models.CharField(max_length=250, blank=True, null=True)
    ip_at_registration = models.CharField(max_length=250, blank=True, null=True)
    ip_at_last_login = models.CharField(max_length=250, blank=True, null=True)
    last_message_at = models.DateTimeField(blank=True, null=True)
    last_message_checking_at = models.DateTimeField(blank=True, null=True)
    last_activity_at = models.DateTimeField(blank=True, null=True)
    latest_votes = models.TextField(blank=True)
    latest_comments = models.TextField(blank=True)
    number_of_comments = models.PositiveIntegerField(default=0)
    number_of_ratings = models.PositiveIntegerField(default=0)
    number_of_messages = models.PositiveIntegerField(default=0)
    number_of_wishes_yes = models.PositiveIntegerField(default=0)
    number_of_wishes_no = models.PositiveIntegerField(default=0)
    number_of_wishes_get = models.PositiveIntegerField(default=0)
    number_of_toplists = models.PositiveIntegerField(default=0)
    number_of_reviews = models.PositiveIntegerField(default=0)
    number_of_bios = models.PositiveIntegerField(default=0)
    number_of_links = models.PositiveIntegerField(default=0)
    bio = models.TextField(blank=True)
    bio_html = models.TextField(blank=True)
    bio_snippet = models.TextField(blank=True)
    fav_period = models.CharField(max_length=250, blank=True, null=True)
    number_of_ratings_1 = models.PositiveIntegerField(default=0)
    number_of_ratings_2 = models.PositiveIntegerField(default=0)
    number_of_ratings_3 = models.PositiveIntegerField(default=0)
    number_of_ratings_4 = models.PositiveIntegerField(default=0)
    number_of_ratings_5 = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(default=None, max_digits=2, decimal_places=1, blank=True, null=True)
    number_of_film_comments = models.PositiveIntegerField(default=0)
    number_of_topic_comments = models.PositiveIntegerField(default=0)
    number_of_poll_comments = models.PositiveIntegerField(default=0)
    number_of_vapiti_votes = models.PositiveIntegerField(default=0)
    vapiti_weight = models.PositiveIntegerField(default=0)
    profile_pic = models.ForeignKey('Picture', blank=True, null=True, related_name='profile_pic', on_delete=models.SET_NULL)
    number_of_followers = models.PositiveIntegerField(default=0)
    opinion_leader = models.BooleanField(default=False)
    design_version = models.PositiveSmallIntegerField(default=1)
    subscribed_to_campaigns = models.BooleanField(default=False)
    token_to_unsubscribe = models.CharField(max_length=64, blank=True)
    unread_notification_count = models.PositiveIntegerField(default=0)
    last_uur_calculation_at = models.DateTimeField(blank=True, null=True)
    signed_privacy_policy = models.BooleanField(default=False)
    signed_privacy_policy_at = models.DateTimeField(blank=True, null=True)

    objects = UserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def email_user(self, subject, html_message, text_message=None, to_email=None, email_type='', campaign_id=0, html_ps='', text_ps='', from_email=settings.DEFAULT_FROM_EMAIL, **kwargs):
        from .misc import EmailCampaign, EmailSend
        if to_email is None:
            to_email = self.email
        if text_message is None:
            text_message = strip_tags(html_message.replace('</p>\n<p>', '\n\n'))
        if campaign_id:
            html_unsub_ps = texts.EMAIL_UNSUB_PS_HTML.format(
                user_id=self.id,
                token=self.token_to_unsubscribe,
                type=email_type,
                campaign_id=campaign_id,
            )
            unsub_ps = texts.EMAIL_UNSUB_PS_TEXT.format(
                user_id=self.id,
                token=self.token_to_unsubscribe,
                type=email_type,
                campaign_id=campaign_id,
            )
        else:
            html_unsub_ps = ''
            unsub_ps = ''
        html_content = texts.EMAIL_TEMPLATE_HTML.format(
            username=self.username,
            html_message=html_message,
            user_id=self.id,
            type=email_type,
            campaign_id=campaign_id,
            ps=html_ps,
            unsub_ps=html_unsub_ps,
        )
        text_content = texts.EMAIL_TEMPLATE_TEXT.format(
            username=self.username,
            text_message=text_message,
            ps=text_ps,
            unsub_ps=unsub_ps,
        )
        email = EmailMultiAlternatives(
            subject,
            text_content,
            from_email,
            [to_email],
        )
        email.attach_alternative(html_content, 'text/html')
        if settings.LOCAL_MAIL or settings.ENV == 'local':
            print '[SUBJECT] {}'.format(email.subject.encode('utf-8'))
            print '[FROM] {}'.format(email.from_email)
            print '[TO] {}'.format(to_email)
            print '[BODY]'
            print email.body.encode('utf-8')
            print '[/BODY]'
            print '[HTML]'
            print html_content.encode('utf-8')
            print '[/HTML]'
        else:
            success = email.send()
            if campaign_id:
                try:
                    campaign = EmailCampaign.objects.get(id=campaign_id)
                except EmailCampaign.DoesNotExist:
                    campaign = None
            else:
                campaign = None
            EmailSend.objects.create(
                user=self,
                email_type=email_type,
                campaign=campaign,
                email=to_email,
                is_pm=True,
                is_email=True,
                is_success=success,
            )

    def votes(self):
        return self.vote_set.all()

    def get_follows(self):
        return self.follow.all()

    def get_followed_by(self):
        return [u.who for u in self.followed_by.all().select_related('who')]

    def save(self, *args, **kwargs):
        self.slug_cache = slugify(self.username)
        self.bio = strip_tags(self.bio)
        self.bio_html = kt_utils.bbcode_to_html(self.bio)
        self.bio_snippet = strip_tags(self.bio_html)[:500]
        if self.token_to_unsubscribe == '':
            self.token_to_unsubscribe = get_random_string(64, allowed_chars='abcdefghijklmnopqrstuvwxyz0123456789')
        super(KTUser, self).save(*args, **kwargs)

    @classmethod
    def get_user_by_name(cls, name):  # case and more importantly accent sensitive getter
        user_list = [user for user in cls.objects.filter(username=name) if user.username == name]
        if user_list:
            return user_list[0]
        return None


class PasswordToken(models.Model):
    token = models.CharField(max_length=64, unique=True)
    belongs_to = models.ForeignKey(KTUser)
    valid_until = models.DateTimeField()

    @classmethod
    def get_token(cls, token_value):  # case sensitive getter
        token_list = [token for token in cls.objects.filter(token=token_value) if token.token == token_value]
        if token_list:
            return token_list[0]
        return None


class UserFavourite(models.Model):
    user = models.ForeignKey(KTUser)
    DOMAIN_FILM = 'F'
    DOMAIN_DIRECTOR = 'D'
    DOMAIN_ACTOR = 'A'
    DOMAIN_GENRE = 'G'
    DOMAIN_COUNTRY = 'C'
    DOMAIN_PERIOD = 'P'
    DOMAINS = [
        (DOMAIN_FILM, 'Film'),
        (DOMAIN_DIRECTOR, 'Director'),
        (DOMAIN_ACTOR, 'Actor'),
        (DOMAIN_GENRE, 'Genre'),
        (DOMAIN_COUNTRY, 'Country'),
        (DOMAIN_PERIOD, 'Period'),
    ]
    domain = models.CharField(max_length=1, choices=DOMAINS, default=DOMAIN_FILM)
    fav_id = models.PositiveIntegerField()

    class Meta:
        unique_together = ['user', 'domain', 'fav_id']


class ProfileSegment(models.Model):
    dimension = models.CharField(max_length=250, blank=True, null=True)
    segment = models.PositiveIntegerField()
    effective_number_of_films = models.PositiveIntegerField(default=0)
    ratio_of_films = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ['dimension', 'segment']

    def __unicode__(self):
        return u'%s:%s' % (self.dimension, self.segment)


class UserProfileSegment(models.Model):
    user = models.ForeignKey(KTUser)
    segment = models.ForeignKey(ProfileSegment)
    number_of_votes = models.PositiveIntegerField(default=0)
    relative_number_of_votes = models.PositiveIntegerField(default=0)
    ratio_of_films = models.PositiveIntegerField(default=0)
    score = models.IntegerField(default=0)

    class Meta:
        unique_together = ['user', 'segment']


class UserContribution(KTUser):
    count_film = models.PositiveIntegerField(default=0)
    rank_film = models.PositiveIntegerField(default=0)
    count_role = models.PositiveIntegerField(default=0)
    rank_role = models.PositiveIntegerField(default=0)
    count_keyword = models.PositiveIntegerField(default=0)
    rank_keyword = models.PositiveIntegerField(default=0)
    count_picture = models.PositiveIntegerField(default=0)
    rank_picture = models.PositiveIntegerField(default=0)
    count_trivia = models.PositiveIntegerField(default=0)
    rank_trivia = models.PositiveIntegerField(default=0)
    count_quote = models.PositiveIntegerField(default=0)
    rank_quote = models.PositiveIntegerField(default=0)
    count_review = models.PositiveIntegerField(default=0)
    rank_review = models.PositiveIntegerField(default=0)
    count_link = models.PositiveIntegerField(default=0)
    rank_link = models.PositiveIntegerField(default=0)
    count_biography = models.PositiveIntegerField(default=0)
    rank_biography = models.PositiveIntegerField(default=0)
    count_poll = models.PositiveIntegerField(default=0)
    rank_poll = models.PositiveIntegerField(default=0)
    count_usertoplist = models.PositiveIntegerField(default=0)
    rank_usertoplist = models.PositiveIntegerField(default=0)
