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


class LoggingMiddleware(object):

    def process_request(self, request):
        utcnow = datetime.datetime.utcnow()
        kutma = request.COOKIES.get('kutma', '')
        if kutma == '':
            kutma = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(32))
        cohort = int(hashlib.md5(kutma).hexdigest(), 16) % 100
        if request.user.is_authenticated():
            request.user.last_activity_at = datetime.datetime.now()
            request.user.save(update_fields=['last_activity_at'])
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
            'user_id': request.user.id if request.user.id else 0,
            'user_name': request.user.username,
            'session': request.session.session_key,
            'kutma': kutma,
            'cohort': cohort,
        })
        request.session['received_time'] = time.time()
        request.session['kutma'] = kutma
        request.session['cohort'] = cohort

    def process_response(self, request, response):
        utcnow = datetime.datetime.utcnow()
        response_time = None
        kutma = None
        cohort = None
        try:
            if 'received_time' in request.session:
                response_time = time.time() - request.session['received_time']
            if 'kutma' in request.session:
                kutma = request.session['kutma']
            if 'cohort' in request.session:
                cohort = request.session['cohort']
        except AttributeError:  # for some redirects there's no request.session
            pass
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
            'user_id': request.user.id if request.user.id else 0,
            'user_name': request.user.username,
            'session': request.session.session_key,
            'kutma': kutma,
            'cohort': cohort,
            'response_time_ms': 1000.0 * response_time if response_time else None,
            'response_status_code': response.status_code,
        })
        if kutma:
            response.set_cookie('kutma', kutma, max_age=SECONDS_IN_A_YEAR, domain='.kritikustomeg.org')
            # response.set_cookie('kutma', kutma, max_age=SECONDS_IN_A_YEAR)
        return response

    def process_exception(self, request, exc):
        kt_exception_logger.exception(u'-----\nDATETIME={dt}\nURL={url}\nUSER_ID={user_id}\nUSER_NAME={user_name}'.format(
            dt=datetime.datetime.strftime(datetime.datetime.utcnow(), '%Y-%m-%d %H:%M:%S.%f'),
            url=request.get_full_path(),
            user_id=request.user.id if request.user.id else 0,
            user_name=request.user.username,
        ).encode('utf-8', errors='ignore'))
