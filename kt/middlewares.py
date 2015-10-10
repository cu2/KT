import datetime
import hashlib
import json
import logging
import random
import string
import time
from ipware.ip import get_ip


kt_pageview_logger = logging.getLogger('kt_pageview')
kt_loadtime_logger = logging.getLogger('kt_loadtime')
kt_exception_logger = logging.getLogger('kt_exception')


SECONDS_IN_A_YEAR = 31536000  # = 365*24*60*60


def jsonlog(logger, level, payload):
    logger.log(level, json.dumps(payload, sort_keys=True))


def randomstring(length):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))


class LoggingMiddleware(object):

    def process_request(self, request):
        utcnow = datetime.datetime.utcnow()
        kutma = request.COOKIES.get('kutma', '')
        if kutma == '':
            kutma = randomstring(32)
        cohort = int(hashlib.md5(kutma).hexdigest(), 16) % 100
        request_id = '%s_%s_%s' % (utcnow.strftime('%Y%m%d-%H%M%S%f'), kutma, randomstring(8))
        user_id = 0
        username = ''
        try:
            if request.user.is_authenticated():
                request.user.last_activity_at = datetime.datetime.now()
                request.user.save(update_fields=['last_activity_at'])
                user_id = request.user.id
                username = request.user.username
        except AttributeError:
            pass
        session_key = ''
        try:
            session_key = request.session.session_key
        except AttributeError:
            pass
        ip = get_ip(request)
        jsonlog(kt_pageview_logger, logging.INFO, {
            'utc_timestamp': utcnow.strftime('%s.%f'),
            'utc_datetime': utcnow.strftime('%Y-%m-%d %H:%M:%S.%f'),
            'ip': ip if ip else '',
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'url': request.get_full_path(),
            'referer': request.META.get('HTTP_REFERER', ''),
            'query_string': request.META.get('QUERY_STRING', ''),
            'request_method': request.META.get('REQUEST_METHOD', ''),
            'server_name': request.META.get('SERVER_NAME', ''),
            'user_id': user_id,
            'user_name': username,
            'session': session_key,
            'kutma': kutma,
            'cohort': cohort,
            'request_id': request_id,
        })
        request.META['KT_RECEIVE_TIME'] = time.time()
        request.META['KT_KUTMA'] = kutma
        request.META['KT_COHORT'] = cohort
        request.META['KT_REQUEST_ID'] = request_id

    def process_response(self, request, response):
        utcnow = datetime.datetime.utcnow()
        user_id = 0
        username = ''
        try:
            if request.user.is_authenticated():
                user_id = request.user.id
                username = request.user.username
        except AttributeError:
            pass
        session_key = ''
        try:
            session_key = request.session.session_key
        except AttributeError:
            pass
        response_time = None
        if 'KT_RECEIVE_TIME' in request.META:
            response_time = time.time() - request.META['KT_RECEIVE_TIME']
        kutma = request.META.get('KT_KUTMA', None)
        cohort = request.META.get('KT_COHORT', None)
        request_id = request.META.get('KT_REQUEST_ID', None)
        ip = get_ip(request)
        jsonlog(kt_loadtime_logger, logging.INFO, {
            'utc_timestamp': utcnow.strftime('%s.%f'),
            'utc_datetime': utcnow.strftime('%Y-%m-%d %H:%M:%S.%f'),
            'ip': ip if ip else '',
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'url': request.get_full_path(),
            'referer': request.META.get('HTTP_REFERER', ''),
            'query_string': request.META.get('QUERY_STRING', ''),
            'request_method': request.META.get('REQUEST_METHOD', ''),
            'server_name': request.META.get('SERVER_NAME', ''),
            'user_id': user_id,
            'user_name': username,
            'session': session_key,
            'kutma': kutma,
            'cohort': cohort,
            'request_id': request_id,
            'response_time_ms': 1000.0 * response_time if response_time else None,
            'response_status_code': response.status_code,
        })
        if kutma:
            response.set_cookie('kutma', kutma, max_age=SECONDS_IN_A_YEAR, domain='.kritikustomeg.org')
        return response

    def process_exception(self, request, exc):
        user_id = 0
        username = ''
        try:
            if request.user.is_authenticated():
                user_id = request.user.id
                username = request.user.username
        except AttributeError:
            pass
        kt_exception_logger.exception(u'-----\nDATETIME={dt}\nURL={url}\nUSER_ID={user_id}\nUSER_NAME={user_name}'.format(
            dt=datetime.datetime.strftime(datetime.datetime.utcnow(), '%Y-%m-%d %H:%M:%S.%f'),
            url=request.get_full_path(),
            user_id=user_id,
            user_name=username,
        ).encode('utf-8', errors='ignore'))
