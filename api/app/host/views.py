import MySQLdb
from flask import Response, request

from core.view import MethodView
from db import get_db
from . import bp_host


@bp_host.route('/index', methods=['GET', 'POST'])
def index():
    return Response("Ok", 500)


class HostTypeView(MethodView):
    # @login_required
    def get(self):
        db = get_db()
        course = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        course.execute('select * from host_type order by `id`')
        query_dict = course.fetchall()
        return Response({"data": list(query_dict), "status": 0})


class HostView(MethodView):
    # @login_required
    def get(self):
        db = get_db()
        course = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        course.execute('select host.*,host_type.name as host_type_name from host left JOIN  host_type on host.host_type_id=host_type.id order by `id`')
        query_dict = course.fetchall()
        return Response({"data": list(query_dict), "status": 0})

    def post(self) -> object:
        """

        :rtype: object
        """
        data = request.json
        pk = data.get("id")
        host_type = data.get("host_type")
        name = data.get("name")
        ip = data.get("ip")
        remark = data.get("remark")

        db = get_db()
        course = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        if pk:
            course.execute('update host set host_type_id=%s,name=%s,ip=%s,remark=%s where id=%s ', (host_type, name, ip, remark, pk))
        else:
            course.execute('insert into host(host_type_id,name,ip,remark) values(%s,%s,%s,%s)',
                           (host_type, name, ip, remark))

        db.commit()
        return Response({"data": list([]), "status": 0})

    def put(self):
        data = request.json
        host_type = data.get("host_type")
        name = data.get("name")
        ip = data.get("ip")
        remark = data.get("remark")
        pk = self.request.values.get("id")
        db = get_db()
        course = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        course.execute('update host set host_type_id=%s,name=%s,ip=%s,remark=%s where id=%s ',
                           (host_type, name, ip, remark, pk))
        db.commit()
        return self.response_ok()

    def delete(self):
        pk = self.request.values.get("id")
        db = get_db()
        course = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        course.execute('delete from  host where id=%s ', (pk,))
        db.commit()
        return self.response_ok()


class NginxView(MethodView):
    pass