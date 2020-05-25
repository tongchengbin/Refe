import MySQLdb

from flask import request, Response

from core.cache import get_cache
from db import get_db


def login_required(f):
    # @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return Response({"msg": "权限验证失败", "status": 400})
        cache = get_cache()
        user_id = cache.get("TOKEN:%s" % token, pick=True)
        if not user_id:
            return Response({"msg": "权限验证失败", "status": 400})
        db = get_db()
        course = db.cursor(cursorclass = MySQLdb.cursors.DictCursor)
        course.execute('select id,username,avatar,is_active from user where id=%s',(user_id,))
        user = course.fetchone()
        request.user_id = user_id
        request.username = user["username"]
        return f(*args, **kwargs)

    return decorated_function


class AdminTokenAuth(object):
    def __init__(self, func):
        self._func = func

    def __call__(self):
        print("____")
        # print(request)
        self._func()

    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def __str__(self):
        return "AdminTokenAuth"
