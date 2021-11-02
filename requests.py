from js import XMLHttpRequest
import json


class Response:
    def __init__(self, data):
        self.raw = data
        self.text = str(data)
    
    def json(self):
        return json.loads(self.raw)


def get(url, **kwargs):
    request = XMLHttpRequest.new()
    request.open("GET", url, False)
    return Response(request.response)


def post(url, **kwargs):
    request = XMLHttpRequest.new()
    request.open("POST", url, False)
    return Response(request.response)
