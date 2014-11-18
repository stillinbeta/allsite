import json
import os
import sys
import traceback

from tornado.httpclient import AsyncHTTPClient, HTTPError
from tornado.httputil import HTTPServerRequest
import tornado.ioloop
import tornado.log

ROLLBAR_URL = 'https://api.rollbar.com/api/1/item/'

logger = tornado.log.gen_log

def _parse_request(request):
    dict_ = {
        'body': str(request.body, 'utf8'),
        'method': request.method,
        'headers': dict(request.headers),
    }


    if isinstance(request, HTTPServerRequest):
        dict_.update({
            'url': request.full_url(),
            'user_ip': request.remote_ip,
            'start_time': getattr(request, '_start_time', None),
        })
    else:
        dict_['url'] = request.url

    return dict_

def _handle(f):
        try:
            res = f.result()
            logger.info("Reported exception:" + str(res.body, 'utf8'))
        except HTTPError:
            logger.info("Error reporting exception", exc_info=True)

def report_error(**kwargs):
    """
    Report an error to Rollbar

    assumes ROLLBAR_TOKEN is in the environment
    also looks for ENVIRONMENT, which defaults to development.

    :exc_info: if given, will be used instead of sys.exc_info()
    :request: a HTTPServerRequest or HTTPRequest
    """

    token = os.environ.get('ROLLBAR_TOKEN')
    env = os.environ.get('ENVIRONMENT', 'development')

    if token is None:
        logger.error("no rollbar token, skipping error reporting")
        return

    exc_info = kwargs.pop('exc_info', None)
    if exc_info is None:
        exc_info = sys.exc_info()

    cls, exc, trace = exc_info

    raw_frames = traceback.extract_tb(trace)
    frames = [{'filename': f[0], 'lineno': f[1], 'method': f[2], 'code': f[3]} for f in raw_frames]

    payload = {
        'access_token': token,
        'data': {
            'environment': env,
            'body': {
                'trace': {
                    'frames': frames,
                    'exception': {
                        'class': cls.__name__,
                        'message': str(exc)
                    },
                },
            },

        }
    }

    if hasattr(exc, 'response'):
        response = exc.response
        payload['data']['custom'] = {
            'request': _parse_request(response.request),
            'response': {
                'code': response.code,
                'headers': response.headers,
                'body': str(response.body, 'utf8'),
                'url': response.effective_url,
            }
        }

    if 'request' in kwargs:
        payload['data']['request'] = _parse_request(kwargs['request'])

    logger.error("Reporting error")
    client = AsyncHTTPClient()
    f = client.fetch(ROLLBAR_URL,
                     method='POST',
                     headers={'Content-type': 'application/json'},
                     body=json.dumps(payload))


    ioloop = tornado.ioloop.IOLoop.instance()
    ioloop.add_future(f, _handle)


