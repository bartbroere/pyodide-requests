"""
Drop-in replacement for the requests module for Pyodide.
Not intended for use with normal CPython, as it depends on the js proxy provided by pyodide.

Don't expect this to be fully feature complete with the original Python requests module.
It aims to cover the most common uses.
"""
import json
from collections import Mapping
from urllib.parse import urlencode
from .status_codes import codes

from js import Blob, XMLHttpRequest


class Response:
    def __init__(self, request):
        self.raw = request.response  # TODO make this a bytestring, as it is in the real requests library
        self.text = str(request.response)
        self.status_code = request.status
        self.headers = request.getAllResponseHeaders()  # TODO turn this into a Case INseNSiTive DicT

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


def _set_headers(request, headers):
    assert isinstance(headers, Mapping)
    for header, value in headers.items():
        request.setRequestHeader(header, value)
    return request


# avoid optimizing imports away (TODO something with __all__)
assert codes
