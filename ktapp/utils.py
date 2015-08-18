import datetime
import re

from django.contrib.auth import authenticate
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied


def bbcode_to_html(value):
    value = re.sub('\[link=([^\]]*)\]', '<a href="\\1">', value)
    value = value.replace('[/link]', '</a>')
    value = value.replace('[b]', '<b>')
    value = value.replace('[/b]', '</b>')
    value = value.replace('[i]', '<i>')
    value = value.replace('[/i]', '</i>')
    value = value.replace('[u]', '<u>')
    value = value.replace('[/u]', '</u>')
    value = value.replace('[del]', '<del>')
    value = value.replace('[/del]', '</del>')
    value = value.replace('[spoiler]', '<span class="spoiler">')
    value = value.replace('[/spoiler]', '</span>')
    value = re.sub('\[img\]([^\]]*)\[/img\]', '<img src="\\1" class="comment_img" />', value)
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


def strip_whitespace(value):
    return value.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ').strip()


def check_permission(perm, user, silent=True):
    if user.is_authenticated():
        grp = {
            'new_quote': 'core',
            'new_trivia': 'core',
            'new_review': 'core',
            'approve_review': 'admin',
            'new_picture': 'core',
            'edit_picture': 'core',
            'delete_picture': 'admin',
            'new_film': 'core',
            'edit_film': 'core',
            'edit_artist': 'core',
            'merge_artist': 'admin',
            'approve_bio': 'admin',
            'edit_role': 'core',
            'new_role': 'core',
            'delete_role': 'core',
            'new_topic': 'core',
        }.get(perm, perm)
        if grp == 'admin' and user.is_staff:
            return True
        if grp == 'core' and user.core_member:
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
