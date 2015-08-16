import datetime
import json
import logging
import time
from ipware.ip import get_ip


kt_pageview_logger = logging.getLogger('kt_pageview')
kt_loadtime_logger = logging.getLogger('kt_loadtime')
kt_exception_logger = logging.getLogger('kt_exception')


def jsonlog(logger, level, payload):
    logger.log(level, json.dumps(payload, sort_keys=True))


class LoggingMiddleware(object):

    def process_request(self, request):
        ip = get_ip(request)
        jsonlog(kt_pageview_logger, logging.INFO, {
            'datetime': datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S'),
            'ip': ip if ip else '',
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'url': request.get_full_path(),
            'referer': request.META.get('HTTP_REFERER', ''),
            'query_string': request.META.get('QUERY_STRING', ''),
            'request_method': request.META.get('REQUEST_METHOD', ''),
            'server_name': request.META.get('SERVER_NAME', ''),
            'user_id': request.user.id if request.user.id else 0,
            'user_name': request.user.username,
        })
        request.session['received_time'] = time.time()

    def process_response(self, request, response):
        try:
            if 'received_time' in request.session:
                response_time = time.time() - request.session['received_time']
                ip = get_ip(request)
                jsonlog(kt_loadtime_logger, logging.INFO, {
                    'datetime': datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S'),
                    'ip': ip if ip else '',
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                    'url': request.get_full_path(),
                    'referer': request.META.get('HTTP_REFERER', ''),
                    'query_string': request.META.get('QUERY_STRING', ''),
                    'request_method': request.META.get('REQUEST_METHOD', ''),
                    'server_name': request.META.get('SERVER_NAME', ''),
                    'user_id': request.user.id if request.user.id else 0,
                    'user_name': request.user.username,
                    'response_time_ms': 1000.0 * response_time,
                    'response_status_code': response.status_code,
                })
        except AttributeError:  # for some redirects there's no request.session
            pass
        return response

    def process_exception(self, request, exc):
        kt_exception_logger.exception(u'-----\nDATETIME={dt}\nURL={url}\nUSER_ID={user_id}\nUSER_NAME={user_name}\nEXCEPTION={exc}'.format(
            dt=datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S'),
            url=request.get_full_path(),
            user_id=request.user.id if request.user.id else 0,
            user_name=request.user.username,
            exc=exc,
        ).encode('utf-8'))
