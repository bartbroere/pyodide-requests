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
import json as json_module  # Renamed to avoid unintentional shadowing by the json parameter in the request() method
from collections.abc import Mapping
from email.parser import Parser
from urllib.parse import urlencode

from js import Blob, XMLHttpRequest

from .exceptions import *
from .hooks import default_hooks
from .status_codes import *
from .structures import CaseInsensitiveDict

DEFAULT_REDIRECT_LIMIT = 30


class Session:
    """
    No-op context manager for packages that rely on requests.Session.

    It has been made entirely no-op because the browser will handle cookies, headers etc., unless explicitly set by
    the user of this requests version.

    """
    __attrs__ = [
        'headers', 'cookies', 'auth', 'proxies', 'hooks', 'params', 'verify',
        'cert', 'prefetch', 'adapters', 'stream', 'trust_env',
        'max_redirects',
    ]

    def __init__(self):

        self.headers = CaseInsensitiveDict({})
        self.auth = None
        self.proxies = {}
        self.hooks = default_hooks()
        self.params = {}
        self.stream = False
        self.verify = True
        self.cert = None
        self.max_redirects = DEFAULT_REDIRECT_LIMIT
        self.trust_env = True
        self.cookies = {}
        self.adapters = {}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        ...

    def get(self, *a, **k):
        return get(*a, **k)

    def post(self, *a, **k):
        return post(*a, **k)

    def head(self, *a, **k):
        return head(*a, **k)

    def options(self, *a, **k):
        return options(*a, **k)

    def put(self, *a, **k):
        return put(*a, **k)

    def delete(self, *a, **k):
        return delete(*a, **k)

    def patch(self, *a, **k):
        return patch(*a, **k)

    def request(self, *a, **k):
        return request(*a, **k)


class Response:
    def __init__(self, request):
        if request.responseType == 'blob':
            self.raw = bytes(request.response.arrayBuffer().result().to_py())
        else:
            self.text = str(request.response)
            self.raw = str(request.response)
        self.status_code = request.status
        try:
            self.headers = CaseInsensitiveDict(Parser().parsestr(request.getAllResponseHeaders(), headersonly=True))
        except TypeError as e:
            # TODO Sometimes this raises TypeError: parsestr() missing 1 required positional argument: 'text'
            #      Find out why and fix, but continue without headers for now
            self.headers = CaseInsensitiveDict({})
            print(e)

    def json(self):
        return json_module.loads(self.text)

    def iter_content(self, *a, **k):
        yield self.raw


def request(method, url,
            params=None, data=None, headers=None, cookies=None, files=None,
            auth=None, timeout=None, allow_redirects=True, proxies=None,
            hooks=None, stream=None, verify=None, cert=None, json=None):
    request = XMLHttpRequest.new()
    if params:
        if isinstance(params, Mapping):
            url = url + '?' + urlencode(params)
    request.open(method.upper(), url, False)
    if headers:
        _set_headers(request, headers)
    if cookies:
        ...  # TODO set the cookie in the browser, otherwise we rely on the cookies the browser decides to send
    if stream:
        request.responseType = "blob"
    if data:
        if isinstance(data, Mapping):
            data = Blob.new([json_module.dumps(data)], {
                'type': 'application/json',
            })
            request.setRequestHeader('Content-Type', 'application/json')
            request.send(data)
        else:
            ...
    if json:
        if isinstance(json, Mapping):
            data = Blob.new([json_module.dumps(json)], {
                'type': 'application/json',
            })
            request.setRequestHeader('Content-Type', 'application/json')
            request.send(data)
        else:
            ...
    else:
        request.send()
    return Response(request)


def _set_headers(request, headers):
    assert isinstance(headers, Mapping)
    for header, value in headers.items():
        request.setRequestHeader(header, value)
    return request


__all__ = [
    'adapters',
    'hooks',
    'codes',
    'get',
    'post',
    'patch',
    'put',
    'delete',
    'request',
    'options',
    'head',
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
    "utils",
    "sessions",
]

# To get a mostly feature complete requests library, we'll eventually need this in __all__ and implemented correctly
# dir(requests)
# ['ConnectTimeout', 'ConnectionError', 'DependencyWarning', 'FileModeWarning', 'HTTPError', 'NullHandler',
#  'PreparedRequest', 'ReadTimeout', 'Request', 'RequestException', 'RequestsDependencyWarning', 'Response', 'Session',
#  'Timeout', 'TooManyRedirects', 'URLRequired', '__author__', '__author_email__', '__build__', '__builtins__',
#  '__cached__', '__cake__', '__copyright__', '__description__', '__doc__', '__file__', '__license__', '__loader__',
#  '__name__', '__package__', '__path__', '__spec__', '__title__', '__url__', '__version__', '_check_cryptography',
#  '_internal_utils', 'adapters', 'api', 'auth', 'certs', 'chardet', 'check_compatibility', 'codes', 'compat', 'cookies',
#  'delete', 'exceptions', 'get', 'head', 'hooks', 'logging', 'models', 'options', 'packages', 'patch', 'post', 'put',
#  'request', 'session', 'sessions', 'status_codes', 'structures', 'urllib3', 'utils', 'warnings']


# Code below was copied from the original requests library
# Requests
# Copyright 2019 Kenneth Reitz
def get(url, params=None, **kwargs):
    r"""Sends a GET request.
    :param url: URL for the new :class:`Request` object.
    :param params: (optional) Dictionary, list of tuples or bytes to send
        in the query string for the :class:`Request`.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    kwargs.setdefault('allow_redirects', True)
    return request('get', url, params=params, **kwargs)


def options(url, **kwargs):
    r"""Sends an OPTIONS request.
    :param url: URL for the new :class:`Request` object.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    kwargs.setdefault('allow_redirects', True)
    return request('options', url, **kwargs)


def head(url, **kwargs):
    r"""Sends a HEAD request.
    :param url: URL for the new :class:`Request` object.
    :param \*\*kwargs: Optional arguments that ``request`` takes. If
        `allow_redirects` is not provided, it will be set to `False` (as
        opposed to the default :meth:`request` behavior).
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    kwargs.setdefault('allow_redirects', False)
    return request('head', url, **kwargs)


def post(url, data=None, json=None, **kwargs):
    r"""Sends a POST request.
    :param url: URL for the new :class:`Request` object.
    :param data: (optional) Dictionary, list of tuples, bytes, or file-like
        object to send in the body of the :class:`Request`.
    :param json: (optional) json data to send in the body of the :class:`Request`.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    return request('post', url, data=data, json=json, **kwargs)


def put(url, data=None, **kwargs):
    r"""Sends a PUT request.
    :param url: URL for the new :class:`Request` object.
    :param data: (optional) Dictionary, list of tuples, bytes, or file-like
        object to send in the body of the :class:`Request`.
    :param json: (optional) json data to send in the body of the :class:`Request`.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    return request('put', url, data=data, **kwargs)


def patch(url, data=None, **kwargs):
    r"""Sends a PATCH request.
    :param url: URL for the new :class:`Request` object.
    :param data: (optional) Dictionary, list of tuples, bytes, or file-like
        object to send in the body of the :class:`Request`.
    :param json: (optional) json data to send in the body of the :class:`Request`.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    return request('patch', url, data=data, **kwargs)


def delete(url, **kwargs):
    r"""Sends a DELETE request.
    :param url: URL for the new :class:`Request` object.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    return request('delete', url, **kwargs)
