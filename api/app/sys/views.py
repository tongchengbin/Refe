import MySQLdb
from flask import Response, request,current_app

from core.auth import login_required
from core.cache import get_cache
from core.utils import generate_token
from db import get_db
from . import bp_sys


@bp_sys.route("/login", methods=("POST",))
def login():
    username = request.json.get("username")
    password = request.json.get("password")
    db = get_db()
    cursor = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
    cursor.execute("select * from user WHERE username= %s and password=%s", (username, password))
    user = cursor.fetchone()
    if user:
        cache = get_cache()
        token = generate_token()
        cache.set("ID:%s" % (user["id"]), token, pick=True)
        cache.set("TOKEN:%s" % token, user["id"], pick=True)
        user["token"] = token
        user.pop("password")
        return Response({"status": 0, "data": user})
    else:
        return Response({"status": 4003, "msg": "账号密码错误"}, 400)


@bp_sys.route("/info", methods=("get",))
@login_required
def get_info():
    db = get_db()
    course = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
    course.execute('select id,username,avatar,is_active from user where id=%s', (request.user_id,))
    user = course.fetchone()
    return Response({"data": user, "status": 0})
