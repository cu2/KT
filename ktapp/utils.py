# -*- coding: utf-8 -*-

import boto3
import datetime
import hashlib
import imghdr
import json
import re

from django.contrib.auth import authenticate
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

from kt import settings


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
        grp = {
            'new_quote': 'core',
            'new_trivia': 'core',
            'new_review': 'core',
            'approve_review': 'admin',
            'new_picture': 'core',
            'edit_picture': 'core',
            'delete_picture': 'reliable',
            'suggest_film': 'core',
            'new_film': 'reliable',
            'edit_film': 'reliable',
            'edit_premiers': 'admin',
            'edit_artist': 'core',
            'merge_artist': 'admin',
            'approve_bio': 'admin',
            'edit_role': 'core',
            'new_role': 'core',
            'delete_role': 'core',
            'new_topic': 'core',
            'check_changes': 'reliable',
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
        }.get(perm, perm)
        if grp == 'admin' and user.is_staff:
            return True
        if grp == 'reliable' and (user.is_reliable or user.is_staff):
            return True
        if grp == 'core' and (user.core_member or user.is_reliable or user.is_staff):
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


def changelog(model, created_by, action, object, state_before, state_after):
    common_keys = set(state_before.keys()) & set(state_after.keys())
    for key in common_keys:
        if state_after[key] == state_before[key]:
            del state_before[key]
            del state_after[key]
    if len(state_before) + len(state_after):
        model.objects.create(
            created_by=created_by,
            action=action,
            object=object,
            state_before=myjsondumps(state_before),
            state_after=myjsondumps(state_after),
        )


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
        'film_title_article': 'az' if film.orig_title[:1].lower() in u'aáeéiíoóöőuúüű' else 'a',
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
            category=u'Arany Vapiti a legjobb filmnek jelölés',
        )
        return [nominee_award.film_id for nominee_award in nominee_awards]
    if vapiti_type == 'F':
        nominee_awards = award_model.objects.filter(
            name=u'Vapiti',
            year=vapiti_year,
            category=u'Ezüst Vapiti a legjobb színésznőnek jelölés',
        )
        return [(nominee_award.film_id, nominee_award.artist_id) for nominee_award in nominee_awards]
    if vapiti_type == 'M':
        nominee_awards = award_model.objects.filter(
            name=u'Vapiti',
            year=vapiti_year,
            category=u'Ezüst Vapiti a legjobb színésznek jelölés',
        )
        return [(nominee_award.film_id, nominee_award.artist_id) for nominee_award in nominee_awards]


def upload_file_to_s3(local_name, remote_name):

    def md5(fname):
        hash = hashlib.md5()
        with open(fname, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash.update(chunk)
        return hash.hexdigest()

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
        local_md5 = md5(local_name)
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
