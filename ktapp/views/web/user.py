# -*- coding: utf-8 -*-

import datetime
import math
from ipware.ip import get_ip

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.utils.html import strip_tags
from django.utils.crypto import get_random_string

from ktapp import models
from ktapp import utils as kt_utils
from ktapp import texts


COMMENTS_PER_PAGE = 100
MESSAGES_PER_PAGE = 50


def registration(request):

    def is_valid_email(email):
        try:
            validate_email(email)
        except ValidationError:
            return False
        return True

    next_url = request.GET.get('next', request.POST.get('next', request.META.get('HTTP_REFERER')))
    error_type = ''
    username = kt_utils.strip_whitespace(request.POST.get('username', ''))
    email = kt_utils.strip_whitespace(request.POST.get('email', ''))
    nickname = request.POST.get('nickname', '')
    if request.method == 'POST':
        if nickname != '':
            error_type = 'robot'
        elif username == '':
            error_type = 'name_empty'
        elif ',' in username or ';' in username:
            error_type = 'name_invalid'
        elif email == '':
            error_type = 'email_empty'
        elif not is_valid_email(email):
            error_type = 'email_invalid'
        elif models.KTUser.objects.filter(email=email).count():
            error_type = 'email_taken'
        elif models.KTUser.objects.filter(username=username).count():
            error_type = 'name_taken'
        else:
            password = get_random_string(32)
            user = models.KTUser.objects.create_user(username, email, password)
            ip = get_ip(request)
            user.ip_at_registration = ip
            user.ip_at_last_login = ip
            user.last_activity_at = datetime.datetime.now()
            user.save()
            token = get_random_string(64)
            models.PasswordToken.objects.create(
                token=token,
                belongs_to=user,
                valid_until=datetime.datetime.now() + datetime.timedelta(days=30),
            )
            user.email_user(
                texts.WELCOME_EMAIL_SUBJECT,
                texts.WELCOME_EMAIL_BODY.format(
                    username=user.username,
                    verification_url=request.build_absolute_uri(reverse('verify_email', args=(token,))),
                )
            )
            login(request, kt_utils.custom_authenticate(models.KTUser, username, password))
            models.Message.send_message(
                sent_by=None,
                content=texts.WELCOME_PM_BODY.format(
                    username=user.username,
                    email=user.email,
                    reset_password_url=reverse('reset_password', args=('',)),  # important: don't send the token via pm
                ),
                recipients=[user],
            )
            return HttpResponseRedirect(next_url)
    return render(request, 'ktapp/registration.html', {
        'next': next_url,
        'username': username,
        'email': email,
        'error_type': error_type,
    })


def custom_login(request):
    next_url = request.GET.get('next', request.POST.get('next', request.META.get('HTTP_REFERER')))
    if request.method == 'POST':
        username_or_email = request.POST.get('username', '')
        password = request.POST.get('password', '')
        nickname = request.POST.get('nickname', '')
        error_type = ''
        if nickname != '':
            error_type = 'robot'
            username_or_email = ''
        elif not username_or_email:
            error_type = 'name_empty'
        elif not password:
            error_type = 'password_empty'
        else:
            user = kt_utils.custom_authenticate(models.KTUser, username_or_email, password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    ip = get_ip(request)
                    user.ip_at_last_login = ip
                    user.last_activity_at = datetime.datetime.now()
                    user.save()
                    return HttpResponseRedirect(next_url)
                else:
                    error_type = 'ban'
            else:
                error_type = 'fail'
        return render(request, 'ktapp/login.html', {
            'next': next_url,
            'error_type': error_type,
            'username': username_or_email,
        })
    return render(request, 'ktapp/login.html', {
        'next': next_url,
    })


def verify_email(request, token):
    error_type = ''
    new_password1 = request.POST.get('new_password1', '')
    new_password2 = request.POST.get('new_password2', '')
    nickname = request.POST.get('nickname', '')
    token_object = None
    if len(token) != 64:
        error_type = 'short_token'
    else:
        token_object = models.PasswordToken.get_token(token)
        if token_object:
            if token_object.valid_until < datetime.datetime.now():
                error_type = 'invalid_token'
            else:
                if request.user.id:
                    if request.user.id != token_object.belongs_to.id:
                        logout(request)
                if not token_object.belongs_to.is_active:
                    error_type = 'ban'
        else:
            error_type = 'invalid_token'
    if error_type == '':
        if request.method == 'POST':
            if nickname != '':
                error_type = 'robot'
            elif len(new_password1) < 6:
                error_type = 'new_password_short'
            elif new_password1 != new_password2:
                error_type = 'new_password_mismatch'
            else:
                token_object.belongs_to.set_password(new_password1)
                token_object.belongs_to.validated_email = True
                token_object.belongs_to.save()
                if not request.user.id:
                    login(request, kt_utils.custom_authenticate(models.KTUser, token_object.belongs_to.username, new_password1))
                error_type = 'ok'
                token_object.delete()
    return render(request, 'ktapp/verify_email.html', {
        'error_type': error_type,
    })


def reset_password(request, token):
    error_type = ''
    username_or_email = request.POST.get('username', '')
    email = ''
    nickname = request.POST.get('nickname', '')
    if token == '':
        if request.method == 'POST':
            if nickname != '':
                error_type = 'robot'
                username_or_email = ''
            elif not username_or_email:
                error_type = 'name_empty'
                username_or_email = ''
            else:
                user = None
                try:
                    user = models.KTUser.objects.get(username=username_or_email)
                except models.KTUser.DoesNotExist:
                    try:
                        user = models.KTUser.objects.get(email=username_or_email)
                    except models.KTUser.DoesNotExist:
                        pass
                if user is None:
                    error_type = 'no_user'
                elif not user.is_active:
                    error_type = 'ban'
                else:
                    token = get_random_string(64)
                    models.PasswordToken.objects.create(
                        token=token,
                        belongs_to=user,
                        valid_until=datetime.datetime.now() + datetime.timedelta(hours=24),
                    )
                    user.email_user(
                        texts.PASSWORD_RESET_EMAIL_SUBJECT,
                        texts.PASSWORD_RESET_EMAIL_BODY.format(
                            username=user.username,
                            reset_password_url=request.build_absolute_uri(reverse('reset_password', args=(token,))),
                        )
                    )
                    error_type = 'ok'
                    email = user.email
        return render(request, 'ktapp/reset_password.html', {
            'page_type': 'ask',
            'error_type': error_type,
            'username': username_or_email,
            'email': email,
        })
    new_password1 = request.POST.get('new_password1', '')
    new_password2 = request.POST.get('new_password2', '')
    nickname = request.POST.get('nickname', '')
    token_object = None
    if len(token) != 64:
        error_type = 'short_token'
    else:
        token_object = models.PasswordToken.get_token(token)
        if token_object:
            if token_object.valid_until < datetime.datetime.now():
                error_type = 'invalid_token'
            else:
                if request.user.id:
                    if request.user.id != token_object.belongs_to.id:
                        logout(request)
                if not token_object.belongs_to.is_active:
                    error_type = 'ban'
        else:
            error_type = 'invalid_token'
    if error_type == '':
        if request.method == 'POST':
            if nickname != '':
                error_type = 'robot'
            elif len(new_password1) < 6:
                error_type = 'new_password_short'
            elif new_password1 != new_password2:
                error_type = 'new_password_mismatch'
            else:
                token_object.belongs_to.set_password(new_password1)
                token_object.belongs_to.validated_email = True
                token_object.belongs_to.save()
                if not request.user.id:
                    login(request, kt_utils.custom_authenticate(models.KTUser, token_object.belongs_to.username, new_password1))
                error_type = 'ok'
                token_object.delete()
    return render(request, 'ktapp/reset_password.html', {
        'error_type': error_type,
    })


@login_required
def change_password(request):
    if not request.user.validated_email:
        return HttpResponseRedirect(reverse('user_profile', args=(request.user.id, request.user.slug_cache)))
    error_type = ''
    old_password = request.POST.get('old_password', '')
    new_password1 = request.POST.get('new_password1', '')
    new_password2 = request.POST.get('new_password2', '')
    nickname = request.POST.get('nickname', '')
    if request.method == 'POST':
        if nickname != '':
            error_type = 'robot'
        elif not request.user.check_password(old_password):
            error_type = 'old_password_invalid'
        elif len(new_password1) < 6:
            error_type = 'new_password_short'
        elif new_password1 != new_password2:
            error_type = 'new_password_mismatch'
        else:
            request.user.set_password(new_password1)
            request.user.save()
            return HttpResponseRedirect(reverse('user_profile', args=(request.user.id, request.user.slug_cache)))
    return render(request, 'ktapp/change_password.html', {
        'error_type': error_type,
    })


@login_required
def messages(request):
    messages_qs = models.Message.objects.filter(owned_by=request.user).select_related('sent_by')
    number_of_messages = messages_qs.count()
    try:
        p = int(request.GET.get('p', 0))
    except ValueError:
        p = 0
    if p == 1:
        return HttpResponseRedirect(reverse('messages'))
    max_pages = int(math.ceil(1.0 * number_of_messages / MESSAGES_PER_PAGE))
    if max_pages == 0:
        max_pages = 1
    if p == 0:
        p = 1
    if p > max_pages:
        return HttpResponseRedirect(reverse('messages') + '?p=' + str(max_pages))
    request.user.last_message_checking_at = datetime.datetime.now()
    request.user.save()
    if request.user.is_staff:
        staff_ids = ','.join([str(u.id) for u in models.KTUser.objects.filter(is_staff=True).order_by('id')])
    else:
        staff_ids = ''
    return render(request, 'ktapp/messages.html', {
        'messages': messages_qs.order_by('-sent_at')[(p-1) * MESSAGES_PER_PAGE:p * MESSAGES_PER_PAGE],
        'p': p,
        'max_pages': max_pages,
        'staff_ids': staff_ids,
    })


@login_required
def new_message(request):
    next_url = request.GET.get('next', request.POST.get('next', reverse('messages')))
    if not request.user.validated_email:
        return HttpResponseRedirect(next_url)
    if request.POST:
        raw_content = request.POST['content']
        content = strip_tags(raw_content).strip()
        if len(content) == 0:
            return HttpResponseRedirect(next_url)
        raw_recipients = request.POST['recipients']
        recipients = set()
        for recipient_name in raw_recipients.strip().split(','):
            recipient = models.KTUser.get_user_by_name(recipient_name.strip())
            if recipient is None:
                continue
            recipients.add(recipient)
        if request.user in recipients and len(recipients) > 1:
            recipients.discard(request.user)
        if len(recipients) == 0:
            return HttpResponseRedirect(next_url)
        models.Message.send_message(
            sent_by=request.user,
            content=content,
            recipients=recipients,
        )
        # TODO: check KTUser.email_notification
        # for recipient in recipients:
        #     recipient.email_user(
        #         texts.PM_EMAIL_SUBJECT.format(sent_by=request.user.username),
        #         texts.PM_EMAIL_BODY.format(
        #             username=recipient.username,
        #             sent_by=request.user.username,
        #             content=content,
        #         )
        #     )
        return HttpResponseRedirect(next_url)
    try:
        message_to_reply_to = models.Message.objects.get(id=request.GET.get('r', 0), owned_by=request.user)
    except models.Message.DoesNotExist:
        message_to_reply_to = None
    users = set()
    if message_to_reply_to:
        for recipient in message_to_reply_to.recipients():
            users.add(recipient)
        if message_to_reply_to.sent_by:
            users.add(message_to_reply_to.sent_by)
    else:
        for raw_user_id in request.GET.get('u', '').split(','):
            try:
                user_id = int(raw_user_id.strip())
            except ValueError:
                continue
            try:
                user = models.KTUser.objects.get(id=user_id)
            except models.KTUser.DoesNotExist:
                continue
            users.add(user)
    if request.user in users and len(users) > 1:  # don't send pm to yourself, if there's at least one other recipient
        users.discard(request.user)
    return render(request, 'ktapp/new_message.html', {
        'list_of_recipients': sorted(list(users), key=lambda u: u.username.upper()),
        'message_to_reply_to': message_to_reply_to,
    })
