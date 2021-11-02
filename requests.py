from js import XMLHttpRequest
import json


class Response:
    def __init__(data):
        self.raw = data
        self.text = str(data)
    
    def json():
        return json.loads(self.raw)


def get(url, *args, **kwargs):
    request = XMLHttpRequest.new()
    request.open("GET", url, False)
    return Response(request.response)
    
def post(url, *args, **kwargs):
    request = XMLHttpRequest.new()
    request.open("POST", url, False)
    return Response(request.response)

    
