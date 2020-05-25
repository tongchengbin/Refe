from flask import Response, json


class JsonResponse(Response):
    @classmethod
    def force_type(cls, response, environ=None):
        if isinstance(response.response, (list, dict)):
            response.data = json.dumps(response.response)
            response.content_type = "application/json;charset=utf-8"
        return response

