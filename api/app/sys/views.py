from flask import Response, request, json, jsonify

import MySQLdb

from core.auth import AdminTokenAuth, login_required
from core.utils import generate_token
from db import get_db
from core.cache import get_cache
from . import bp_sys


@bp_sys.route("/login", methods=("POST",))
def login():
    username = request.json.get("username")
    password = request.json.get("password")
    db = get_db()
    cursor = db.cursor(cursorclass = MySQLdb.cursors.DictCursor)
    cursor.execute("select * from user WHERE username= %s and password=%s", (username,password))
    user = cursor.fetchone()
    if user:
        cache = get_cache()
        token = generate_token()
        cache.set("ID:%s" % (user["id"]), token, pick=True)
        cache.set("TOKEN:%s" % token, user["id"], pick=True)
        user["token"] = token
        user.pop("password")
        return Response(user)
    else:
        return Response({"status":4003,"msg":"账号密码错误"},400)


#

@bp_sys.route("/info", methods=("get",))
@login_required
def get_info():
    db = get_db()
    course = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
    course.execute('select id,username,avatar,is_active from user where id=%s', (request.user_id,))
    user = course.fetchone()
    return Response(user)

