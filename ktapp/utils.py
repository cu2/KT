# -*- coding: utf-8 -*-

import boto3
import datetime
import hashlib
import imghdr
import json
import os
import re

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import user_passes_test
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.db import migrations
from django.db.models import Sum

from ktapp import texts


def bbcode_to_html(value):
    value = re.sub('\[link\](http://kritikustomeg.org.*?)\[/link\]', '<a href="\\1">\\1</a>', value, flags=re.S)
    value = re.sub('\[link=\](http://kritikustomeg.org.*?)\[/link\]', '<a href="\\1">\\1</a>', value, flags=re.S)
    value = re.sub('\[link=(http://kritikustomeg.org[^\]]*)\](.*?)\[/link\]', '<a href="\\1">\\2</a>', value, flags=re.S)
    value = re.sub('\[link\](https://kritikustomeg.org.*?)\[/link\]', '<a href="\\1">\\1</a>', value, flags=re.S)
    value = re.sub('\[link=\](https://kritikustomeg.org.*?)\[/link\]', '<a href="\\1">\\1</a>', value, flags=re.S)
    value = re.sub('\[link=(https://kritikustomeg.org[^\]]*)\](.*?)\[/link\]', '<a href="\\1">\\2</a>', value, flags=re.S)
    value = re.sub('\[link\](http://.*?)\[/link\]', '<a href="\\1" target="_blank" rel="nofollow">\\1</a>', value, flags=re.S)
    value = re.sub('\[link=\](http://.*?)\[/link\]', '<a href="\\1" target="_blank" rel="nofollow">\\1</a>', value, flags=re.S)
    value = re.sub('\[link=(http://[^\]]*)\](.*?)\[/link\]', '<a href="\\1" target="_blank" rel="nofollow">\\2</a>', value, flags=re.S)
    value = re.sub('\[link\](https://.*?)\[/link\]', '<a href="\\1" target="_blank" rel="nofollow">\\1</a>', value, flags=re.S)
    value = re.sub('\[link=\](https://.*?)\[/link\]', '<a href="\\1" target="_blank" rel="nofollow">\\1</a>', value, flags=re.S)
    value = re.sub('\[link=(https://[^\]]*)\](.*?)\[/link\]', '<a href="\\1" target="_blank" rel="nofollow">\\2</a>', value, flags=re.S)
    value = re.sub('\[link\](.*?)\[/link\]', '<a href="\\1">\\1</a>', value, flags=re.S)
    value = re.sub('\[link=\](.*?)\[/link\]', '<a href="\\1">\\1</a>', value, flags=re.S)
    value = re.sub('\[link=([^\]]*)\](.*?)\[/link\]', '<a href="\\1">\\2</a>', value, flags=re.S)
    value = re.sub('\[b\](.*?)\[/b\]', '<b>\\1</b>', value, flags=re.S)
    value = re.sub('\[i\](.*?)\[/i\]', '<i>\\1</i>', value, flags=re.S)
    value = re.sub('\[u\](.*?)\[/u\]', '<span class="underlined">\\1</span>', value, flags=re.S)
    value = re.sub('\[del\](.*?)\[/del\]', '<span class="deleted">\\1</span>', value, flags=re.S)
    value = re.sub('\[spoiler\](.*?)\[/spoiler\]', '<span class="spoiler">\\1</span>', value, flags=re.S)
    value = re.sub('\[img\]([^\]]*?)\[/img\]', '<img src="\\1" class="comment_img" />', value, flags=re.S)
    return value


def html_to_bbcode(value):
    value = re.sub('<a href="([^"]*)">', '[link=\\1]', value)
    value = value.replace('</a>', '[/link]')
    value = value.replace('<b>', '[b]')
    value = value.replace('</b>', '[/b]')
    value = value.replace('<i>', '[i]')
    value = value.replace('</i>', '[/i]')
    value = value.replace('<u>', '[u]')
    value = value.replace('</u>', '[/u]')
    value = value.replace('<del>', '[del]')
    value = value.replace('</del>', '[/del]')
    value = value.replace('<div id="SPOIL1">', '[spoiler]')
    value = value.replace('</div>', '[/spoiler]')
    value = re.sub('<img src="([^"]*)">', '[img]\\1[/img]', value)
    return value


def custom_authenticate(user_model, username_or_email, password):
    try:
        user = user_model.objects.get(email=username_or_email)
        username = user.username
    except user_model.DoesNotExist:
        username = username_or_email
    return authenticate(username=username, password=password)


def is_date(value):
    try:
        datetime.datetime.strptime(value, '%Y-%m-%d')
    except ValueError:
        return False
    return True


def is_datetime(value):
    try:
        datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return False
    return True


def strip_whitespace(value):
    return value.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ').strip()


def strip_whitespace_and_separator(value):
    return value.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ').replace(',', ' ').replace(';', ' ').strip()


def check_permission(perm, user, silent=True):
    if user.is_authenticated():
        # hacky way of exceptions:
        if user.id == 4083 and perm in {
            'new_quote', 'edit_quote', 'delete_quote',
            'new_trivia', 'edit_trivia', 'delete_trivia',
        }:
            if silent:
                return False
            raise PermissionDenied
        grp = {
            'new_quote': 'core',
            'edit_quote': 'core',
            'delete_quote': 'core',
            'new_trivia': 'core',
            'edit_trivia': 'core',
            'delete_trivia': 'core',
            'new_review': 'core',
            'approve_review': 'admin',
            'new_picture': 'core',
            'edit_picture': 'core',
            'delete_picture': 'reliable',
            'set_main_picture': 'reliable',
            'suggest_film': 'core',
            'new_film': 'reliable',
            'edit_film': 'reliable',
            'delete_award': 'admin',
            'edit_premiers': 'admin',
            'edit_artist': 'core',
            'merge_artist': 'admin',
            'approve_bio': 'admin',
            'edit_role': 'core',
            'new_role': 'core',
            'delete_role': 'core',
            'new_topic': 'core',
            'check_changes': 'reliable',
            'check_missing_data': 'core',
            'poll_admin': 'admin',
            'new_poll': 'core',
            'suggest_link': 'core',
            'new_link': 'reliable',
            'edit_link': 'reliable',
            'delete_link': 'reliable',
            'vote_vapiti': 'core',
            'new_usertoplist': 'all',
            'edit_usertoplist': 'all',
            'delete_usertoplist': 'all',
            'analytics': 'superuser',
            'logs': 'superuser',
            'move_to_off': 'inner_staff',
            'ban_user': 'inner_staff',
            'see_core': 'inner_staff',
            'edit_iszdb': 'iszdb',
            'set_game_master': 'game_admin',
        }.get(perm, perm)
        if grp == 'superuser' and user.is_superuser:
            return True
        if grp == 'inner_staff' and user.is_inner_staff:
            return True
        if grp == 'admin' and user.is_staff:
            return True
        if grp == 'reliable' and (user.is_reliable or user.is_staff):
            return True
        if grp == 'core' and (user.core_member or user.is_reliable or user.is_staff):
            return True
        if grp == 'iszdb' and user.id in {1, 4256, 16515}:
            return True
        if grp == 'game_admin' and user.id in {1, 13114}:
            return True
        if grp == 'all':
            return True
    if silent:
        return False
    raise PermissionDenied


def kt_permission_required(perm):
    def check_perms(user):
        return check_permission(perm, user, False)
    return user_passes_test(check_perms)


def coalesce(value, default_value):
    if value is None:
        return default_value
    return value


def minmax2interval(min_value, max_value, default_min, default_max):
    if min_value is None:
        if max_value is None:
            return None
        else:
            return (default_min, max_value)
    else:
        if max_value is None:
            return (min_value, default_max)
        else:
            return (min_value, max_value)


def str2interval(value, default_type, default_min=0, default_max=9999):
    if '-' in value:
        min_value, max_value = value.split('-')[:2]
        try:
            min_value = default_type(min_value.strip())
        except:
            min_value = None
        try:
            max_value = default_type(max_value.strip())
        except:
            max_value = None
        return minmax2interval(min_value, max_value, default_min, default_max)

    try:
        value = default_type(value.strip())
    except:
        return None
    return (value, value)


def myjsondumps(value):
    if value is None:
        return ''
    ret = {}
    for key, val in value.iteritems():
        if isinstance(val, unicode):
            ret[key] = val.encode('utf-8')
        if isinstance(val, datetime.date):
            ret[key] = val.strftime('%Y-%m-%d')
        else:
            ret[key] = val
    return json.dumps(ret, sort_keys=True)


def changelog(model, created_by, action, object, state_before, state_after, force=False):
    common_keys = set(state_before.keys()) & set(state_after.keys())
    for key in common_keys:
        if state_after[key] == state_before[key]:
            del state_before[key]
            del state_after[key]
    if len(state_before) + len(state_after) > 0 or force:
        model.objects.create(
            created_by=created_by,
            action=action,
            object=object,
            state_before=myjsondumps(state_before),
            state_after=myjsondumps(state_after),
        )


def picture_index(picture, film):
    if film.main_poster and picture.id == film.main_poster.id:
        return 0, picture.order_key, picture.id
    else:
        return 1, picture.order_key, picture.id


def get_next_picture(pictures, picture):
    found_this = False
    next_picture = None
    for pic in pictures:
        if found_this:
            next_picture = pic
            break
        if pic == picture:
            found_this = True
    if next_picture is None:
        next_picture = pictures[0]
    return next_picture


def get_selected_picture_details(model, film, picture, next_picture):
    return {
        'picture': picture,
        'next_picture': next_picture,
        'pic_height': model.THUMBNAIL_SIZES['max'][1],
        'artists': picture.artists.all(),
        'film_title_article': ('az' if film.orig_title[:1].lower() in u'aáeéiíoóöőuúüű' else 'a') if film else '',
    }


def get_vapiti_round():
    today = datetime.date.today()
    today_str = today.strftime('%Y-%m-%d')
    round_1_dates = (
        '%s-01-01' % (settings.VAPITI_YEAR + 1),
        '%s-01-21' % (settings.VAPITI_YEAR + 1),
    )
    last_day_of_round_2 = [22, 21, 20, 19, 25, 24, 23][datetime.date(settings.VAPITI_YEAR + 1, 2, 19).weekday()]
    result_day = [23, 22, 21, 20, 26, 25, 24][datetime.date(settings.VAPITI_YEAR + 1, 2, 19).weekday()]
    round_2_dates = (
        '%s-01-22' % (settings.VAPITI_YEAR + 1),
        '%s-02-%s' % (settings.VAPITI_YEAR + 1, last_day_of_round_2),
    )
    result_day = '%s-02-%s' % (settings.VAPITI_YEAR + 1, result_day)
    if today_str >= round_1_dates[0] and today_str <= round_1_dates[1]:
        vapiti_round = 1
    elif today_str >= round_2_dates[0] and today_str <= round_2_dates[1]:
        vapiti_round = 2
    elif today_str >= result_day:
        vapiti_round = 3
    else:
        vapiti_round = 0
    return (
        vapiti_round,
        round_1_dates,
        round_2_dates,
        result_day,
    )


def get_vapiti_nominees(award_model, vapiti_type):
    vapiti_year = settings.VAPITI_YEAR
    if vapiti_type == 'G':
        nominee_awards = award_model.objects.filter(
            name=u'Vapiti',
            year=vapiti_year,
            category=texts.VAPITI_NOMINEE_CATEGORIES[vapiti_type],
        )
        return [nominee_award.film_id for nominee_award in nominee_awards]
    if vapiti_type in {'F', 'M'}:
        nominee_awards = award_model.objects.filter(
            name=u'Vapiti',
            year=vapiti_year,
            category=texts.VAPITI_NOMINEE_CATEGORIES[vapiti_type],
        )
        return [(nominee_award.film_id, nominee_award.artist_id) for nominee_award in nominee_awards]



def get_local_md5(fname):
    hash = hashlib.md5()
    with open(fname, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash.update(chunk)
    return hash.hexdigest()


def upload_file_to_s3(local_name, remote_name):

    mime_type = imghdr.what(local_name)
    if mime_type:
        mime_type = 'image/%s' % mime_type
    else:
        mime_type = 'binary/octet-stream'
    key = None
    try:
        boto3_session = boto3.session.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_DEFAULT_REGION,
        )
        s3 = boto3_session.resource('s3')
        local_md5 = get_local_md5(local_name)
        key = s3.Object('kt.static', remote_name)
        key.put(
            Body=open(local_name, 'rb'),
            ContentType=mime_type,
            ContentDisposition='inline',
        )
        remote_md5 = key.e_tag[1:-1]
    except:
        if key:
            try:
                key.delete()
            except:
                pass
        return False
    if key and local_md5 == remote_md5:
        return True
    if key:
        try:
            key.delete()
        except:
            pass
    return False


def download_file_from_s3(remote_name, local_name):

    try:
        boto3_session = boto3.session.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_DEFAULT_REGION,
        )
        s3 = boto3_session.resource('s3')
        remote_md5 = s3.Object('kt.static', remote_name).e_tag[1:-1]
        s3.meta.client.download_file('kt.static', remote_name, local_name)
        local_md5 = get_local_md5(local_name)
    except Exception as e:
        print e
        try:
            os.unlink(local_name)
        except:
            pass
        return False
    if local_md5 == remote_md5:
        return True
    try:
        os.unlink(local_name)
    except:
        pass
    return False


def download_file_from_s3_with_retry(remote_name, local_name, retry_count=2):
    if download_file_from_s3(remote_name, local_name):
        return True
    if retry_count:
        return download_file_from_s3_with_retry(remote_name, local_name, retry_count-1)
    return False


def delete_file_from_s3(remote_name):
    try:
        boto3_session = boto3.session.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_DEFAULT_REGION,
        )
        s3 = boto3_session.resource('s3')
        key = s3.Object('kt.static', remote_name)
        key.delete()
    except:
        pass


def get_finance(model):
    collected_so_far = model.objects.aggregate(Sum('money'))['money__sum']
    if collected_so_far is None:
        collected_so_far = 0
    required_so_far = (datetime.date.today() - datetime.date(2009, 10, 22)).days / 365.0 * 100000.0
    missing = int(round(collected_so_far - required_so_far))
    percent = 100.0 * (missing + 100000) / 100000
    if percent > 100:
        percent = 100
    if percent < 0:
        percent = 0
    return int(round(percent)), missing


def get_banner_version(user_id):
    if user_id is None:
        version = 0
    else:
        version = user_id % 4
    if version == 0:
        return 50, 2000
    elif version == 1:
        return 40, 2500
    elif version == 2:
        return 25, 4000
    else:
        return 20, 5000


def delete_sessions(user_id):
    user_id_string = str(user_id)
    from django.contrib.sessions.models import Session
    for s in Session.objects.all():
        session_user_id = s.get_decoded().get('_auth_user_id')
        if session_user_id == user_id_string or session_user_id == user_id:
            s.delete()


def get_design_version(request):
    if request.user.is_authenticated():
        return request.user.design_version
    return 2
    # # A/B test
    # cohort = request.META.get('KT_COHORT', 0)
    # if cohort < 50:
    #     design_version = 1
    # else:
    #     design_version = 2
    # return design_version


def parse_porthu_link(raw_link):
    if raw_link.isdigit():
        return raw_link
    if 'i_film_id' in raw_link:
        try:
            return int(raw_link[raw_link.index('i_film_id')+10:].split('&')[0])
        except ValueError:
            return None
    if '/movie-' in raw_link:  # new style from 2016 nov
        try:
            return int(raw_link[raw_link.index('/movie-')+7:])
        except ValueError:
            return None
    return None


def create_comment_notifications(source_user, comment, film, topic, poll):
    from ktapp import models
    lately = datetime.datetime.now() - datetime.timedelta(days=30)
    target_users = {}
    # reply
    if comment.reply_to:
        target_users[comment.reply_to.created_by_id] = models.Notification.NOTIFICATION_SUBTYPE_COMMENT_REPLY
    # mention
    # TODO
    if comment.domain == models.Comment.DOMAIN_FILM:
        # commented lately
        for c in models.Comment.objects.filter(domain=models.Comment.DOMAIN_FILM, film=film, created_at__gte=lately):
            target_user_id = c.created_by_id
            if target_user_id not in target_users:
                target_users[target_user_id] = models.Notification.NOTIFICATION_SUBTYPE_COMMENT_ON_FILM_YOU_COMMENTED
        # rated lately
        for v in models.Vote.objects.filter(film=film, when__gte=lately):
            target_user_id = v.user_id
            if target_user_id not in target_users:
                target_users[target_user_id] = models.Notification.NOTIFICATION_SUBTYPE_COMMENT_ON_FILM_YOU_RATED
        # wished lately
        for w in models.Wishlist.objects.filter(wish_type=models.Wishlist.WISH_TYPE_YES, film=film, wished_at__gte=lately):
            target_user_id = w.wished_by_id
            if target_user_id not in target_users:
                target_users[target_user_id] = models.Notification.NOTIFICATION_SUBTYPE_COMMENT_ON_FILM_YOU_WISHED
    for target_user_id, subtype in target_users.iteritems():
        if target_user_id != source_user.id:
            models.Notification.objects.create(
                target_user_id=target_user_id,
                notification_type=models.Notification.NOTIFICATION_TYPE_COMMENT,
                notification_subtype=subtype,
                film=film,
                topic=topic,
                poll=poll,
                source_user=source_user,
                comment=comment,
            )


def run_sql_except_on_sqlite(sql, reverse_sql):
    if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
        return migrations.RunSQL(migrations.RunSQL.noop, migrations.RunSQL.noop)
    return migrations.RunSQL(sql, reverse_sql)


def get_premiers_for_today():
    cached_value = cache.get('get_premiers_for_today')
    print('get_premiers_for_today', cached_value)
    if cached_value is not None:
        return cached_value

    from ktapp import models
    today = datetime.date.today()
    offset = today.weekday()  # this Monday
    from_date = today - datetime.timedelta(days=offset)
    until_date = today - datetime.timedelta(days=offset-6)
    premier_film_list = []
    for film in models.Film.objects.filter(main_premier__gte=from_date, main_premier__lte=until_date):
        premier_film_list.append(film)
    for item in models.Premier.objects.filter(when__gte=from_date, when__lte=until_date).select_related('film'):
        premier_film_list.append(item.film)
    premier_film_list.sort(key=lambda item: (item.orig_title, item.id))

    cache.set('get_premiers_for_today', premier_film_list, timeout=3600)
    return premier_film_list
