from flask import Response, json


class JsonResponse(Response):
    @classmethod
    def force_type(cls, response, environ=None):
        if isinstance(response.response, (list, dict)):
            print(response)
            response.data = json.dumps(response.response,ensure_ascii=False)
            response.content_type = "application/json;charset=utf-8"
        return response

