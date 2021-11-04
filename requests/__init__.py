"""
Drop-in replacement for the requests module for Pyodide.
Not intended for use with normal CPython, as it depends on the js proxy provided by pyodide.

Don't expect this to be fully feature complete with the original Python requests module yet.
It aims to cover the most common uses.

Another important thing to realize is that we rely somewhat on what the browser things a sane request is.
This means that some headers are included by default, even though they might not be specified in the Python code.
It also means cookies are handled mostly by the browser and a bit less by requests.Session.
This way, Python code can use authenticated sessions that already exist in the browser.
"""
import json
from email.parser import Parser
from collections import Mapping
from urllib.parse import urlencode
from .status_codes import *
from .exceptions import *
from .structures import CaseInsensitiveDict

from js import Blob, XMLHttpRequest


class Response:
    def __init__(self, request):
        self.raw = request.response  # TODO make this a bytestring, as it is in the real requests library
        self.text = str(request.response)
        self.status_code = request.status
        self.headers = CaseInsensitiveDict(Parser.parsestr(request.getAllResponseHeaders(), headersonly=True))

    def json(self):
        return json.loads(self.raw)


def get(url, params=None, headers=None, cookies=None, **kwargs):
    request = XMLHttpRequest.new()
    if params:
        if isinstance(params, Mapping):
            url = url + '?' + urlencode(params)
    request.open("GET", url, False)
    if headers:
        _set_headers(request, headers)
    if cookies:
        ...
    request.send()
    return Response(request)


def post(url, data=None, headers=None, cookies=None, **kwargs):
    request = XMLHttpRequest.new()
    request.open("POST", url, False)
    if headers:
        _set_headers(request, headers)
    if cookies:
        ...  # TODO set the cookie in the browser, otherwise we rely on the cookie the browser decides to send
    if data:
        if isinstance(data, Mapping):
            data = Blob.new([json.dumps(data)], {
                'type': 'application/json'
            })
            request.setRequestHeader('Content-Type', 'application/json')
            request.send(data)
        else:
            ...
    else:
        request.send()
    return Response(request)


def patch(url, *args, **kwargs):
    ...


def put(url, *args, **kwargs):
    ...


def delete(url, *args, **kwargs):
    ...


def head(url, *args, **kwargs):
    ...


def _set_headers(request, headers):
    assert isinstance(headers, Mapping)
    for header, value in headers.items():
        request.setRequestHeader(header, value)
    return request


__all__ = [
    'codes',
    'get',
    'post',
    'Response',
    "RequestException",
    "InvalidJSONError",
    "HTTPError",
    "ConnectionError",
    "ProxyError",
    "SSLError",
    "Timeout",
    "ConnectTimeout",
    "ReadTimeout",
    "URLRequired",
    "TooManyRedirects",
    "MissingSchema",
    "InvalidSchema",
    "InvalidURL",
    "InvalidHeader",
    "InvalidProxyURL",
    "ChunkedEncodingError",
    "ContentDecodingError",
    "StreamConsumedError",
    "RetryError",
    "UnrewindableBodyError",
    "RequestsWarning",
    "FileModeWarning",
    "RequestsDependencyWarning",
]

# To get a mostly feature complete requests library, we'll eventually need this in __all__ and implemented
# dir(requests)
# ['ConnectTimeout', 'ConnectionError', 'DependencyWarning', 'FileModeWarning', 'HTTPError', 'NullHandler',
#  'PreparedRequest', 'ReadTimeout', 'Request', 'RequestException', 'RequestsDependencyWarning', 'Response', 'Session',
#  'Timeout', 'TooManyRedirects', 'URLRequired', '__author__', '__author_email__', '__build__', '__builtins__',
#  '__cached__', '__cake__', '__copyright__', '__description__', '__doc__', '__file__', '__license__', '__loader__',
#  '__name__', '__package__', '__path__', '__spec__', '__title__', '__url__', '__version__', '_check_cryptography',
#  '_internal_utils', 'adapters', 'api', 'auth', 'certs', 'chardet', 'check_compatibility', 'codes', 'compat', 'cookies',
#  'delete', 'exceptions', 'get', 'head', 'hooks', 'logging', 'models', 'options', 'packages', 'patch', 'post', 'put',
#  'request', 'session', 'sessions', 'status_codes', 'structures', 'urllib3', 'utils', 'warnings']
