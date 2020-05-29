import MySQLdb
from flask import Response, request

from core.ssh import SshCommand
from core.view import MethodView
from db import get_db
from utils.nginxParser import NginxParser
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
        course.execute(
            'select host.*,host_type.name as host_type_name from host left JOIN  host_type on host.host_type_id=host_type.id order by `id`')
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
            course.execute('update host set host_type_id=%s,name=%s,ip=%s,remark=%s where id=%s ',
                           (host_type, name, ip, remark, pk))
        else:
            course.execute('insert into host(host_type_id,name,ip,remark) values(%s,%s,%s,%s)',
                           (host_type, name, ip, remark))

        db.commit()
        return Response({"data": [], "status": 0})

    def put(self):
        data = request.json
        host_type = data.get("host_type")
        password = data.get("password")
        name = data.get("name")
        ip = data.get("ip")
        remark = data.get("remark")
        pk = self.request.values.get("id")
        db = get_db()
        course = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        course.execute('update host set host_type_id=%s,name=%s,ip=%s,remark=%s,password=%s where id=%s ',
                       (host_type, name, ip, remark, password, pk))
        db.commit()
        return self.response_ok()

    def delete(self):
        pk = self.request.values.get("id")
        db = get_db()
        course = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        course.execute('delete from  host where id=%s ', (pk,))
        db.commit()
        return self.response_ok()


@bp_host.route('/ngFile', methods=['get'])
def read_ng_file():
    ssh = SshCommand('119.23.175.115', password='uhoo!@#^%$')
    results = ssh.get_nginx()
    return Response({"data": results, "status": 0})


@bp_host.route('/ng_website', methods=['get'])
def ng_website():
    ssh = SshCommand('119.23.175.115', password='uhoo!@#^%$')
    results = ssh.get_nginx()

    data = []
    for f, r in results.items():
        nginx = NginxParser()
        nginx.load(r)
        website = nginx.parser_website()
        for w in website:
            w["file"] = f
            data.append(w)
    return Response({"data": data, "status": 0})


@bp_host.route('/process', methods=['get'])
def host_process():
    ssh = SshCommand('119.23.175.115', password='uhoo!@#^%$')
    results = ssh.exec('ps -ef ')
    data = []
    for line in results.split("\n")[1:]:
        ary = line.split()
        if len(ary) < 8:
            continue
        data.append({
            "uid": ary[0],
            "pid": ary[1],
            "ppid": ary[2],
            "c": ary[3],
            "stime": ary[4],
            "tty": ary[5],
            "time": ary[6],
            "cmd": " ".join(ary[7:])
        })
    return Response({"data": data, "status": 0})


@bp_host.route('/code', methods=['get', 'put', 'post'])
def host_code():
    if request.method == 'GET':
        # ssh = SshCommand('119.23.175.115', password='uhoo!@#^%$')
        db = get_db()
        course = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        sql = "select * from server_code"
        course.execute(sql)
        query = course.fetchall()
        return Response({"status": 0, "data": query})
    elif request.method == 'PUT':
        data = request.json
        try:
            pk = data["id"]
            host = data["host_id"]
            name = data["name"]
            branch = data["branch"]
            remark = data.get("remark")
            confirm = data.get("confirm", False)
        except KeyError:
            return Response({"status": 400, "error": "参数异常"})
        db = get_db()
        course = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        course.execute("select * from server_code where id=%s", (pk,))
        code = course.fetchone()
        course.execute("select * from host where id=%s", (host,))
        host_info = course.fetchone()
        if not host_info or not host_info["password"]: return Response({"status": 400, "error": "该主机无法部署"})
        ssh = SshCommand(host_info["ip"], password=host_info["password"])
        # 检测目录是否存在
        res = ssh.exec("cd %s" % code["root"])
        if res: return Response({"status": 400, "error": "目录不存在"})
        # 检测分支
        check_branch = ssh.exec("cd %s && git branch " % code["root"])
        current_branch = [i for i in check_branch.split("\n") if i and str(i).startswith("*")]
        if current_branch:
            current_branch = current_branch[0].replace("*", "").strip()
        else:
            Response({"status": 400, "error": "无法检测当前分支"})
        if current_branch != branch and not confirm:
            # 需要确认
            return Response({"status": 0, "data": {"need_confirm": True}})
        # 开始checkout
        if current_branch != branch:
            ssh.exec('cd %s && git checkout %s' % (code["root"], branch))
        # 开始pull
        res_pull = ssh.exec('cd %s && git checkout . && git pull' % (code["root"],))
        # 更新信息
        commit_info = ssh.exec('cd %s && git log -n 1' % code["root"])
        commit_ary = commit_info.split("\n")
        if len(commit_ary) > 4:
            commit_id = " ".join(commit_ary[0].split()[1:])
            author = " ".join(commit_ary[1].split()[1:])
            commit_dt = " ".join(commit_ary[2].split()[1:])
            commit_con = "".join(commit_ary[2:])
        else:
            commit_id = author = dt_str = commit_con = None
        sql = 'update  server_code set host_id=%s, name=%s,branch=%s,' \
              'remark=%s,commit_id =%s,author = %s,' \
              'commit_dt = %s,commit_con=%s where id= %s'
        course.execute(sql, (host, name, branch, remark, commit_id, author, commit_dt, commit_con, pk))
        db.commit()
        return Response({"status": 0, "data": {}})
    elif request.method == 'POST':
        data = request.json
        try:
            host = data["host_id"]
            name = data["name"]
            branch = data["branch"]
            remark = data.get("remark")
            root = data["root"]
        except KeyError:
            return Response({"status": 400, "error": "参数异常"})
        db = get_db()
        course = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        course.execute("select * from host where id=%s", (host,))
        query_dict = course.fetchone()
        ssh = SshCommand(query_dict["ip"], password=query_dict["password"])
        # 检测目录是否存在
        res = ssh.exec("cd %s" % root)
        if res:
            return Response({"status": 400, "error": "目录不存在"})
        return Response({"status": 400, "error": "功能开发中"})

    else:
        return Response({"status": 400, "error": "功能开发中"})


@bp_host.route('/code_pull', methods=['get'])
def host_code_pull():
    pk = request.values.get("id")
    if not pk: return Response({"status": 400, "error": "参数异常"})
    db = get_db()
    course = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
    course.execute(
        "select host.ip,host.password,root from server_code left  join  host on server_code.host_id= host.id where server_code.id=%s",
        (pk,))
    query_dict = course.fetchone()

    if not query_dict or not query_dict["password"]: return Response({"status": 400, "error": "该主机无法部署"})
    ssh = SshCommand(query_dict["ip"], password=query_dict["password"])
    # 检测目录是否存在
    res = ssh.exec("cd %s" % query_dict["root"])
    if res: return Response({"status": 400, "error": "目录不存在"})
    res_pull = ssh.exec('cd %s && git checkout . && git pull' % (query_dict["root"],))
    # 检测分支
    check_branch = ssh.exec("cd %s && git branch " % query_dict["root"])
    current_branch = [i for i in check_branch.split("\n") if i and str(i).startswith("*")]
    if current_branch:
        current_branch = current_branch[0].replace("*", "").strip()
    # 更新信息
    commit_info = ssh.exec('cd %s && git log -n 1' % query_dict["root"])
    commit_ary = commit_info.split("\n")
    if len(commit_ary) > 4:
        commit_id = " ".join(commit_ary[0].split()[1:])
        author = " ".join(commit_ary[1].split()[1:])
        commit_dt = " ".join(commit_ary[2].split()[1:])
        commit_con = "".join(commit_ary[2:])
    else:
        commit_id = author = dt_str = commit_con = None
    sql = 'update  server_code set branch=%s,commit_id =%s,author = %s,' \
          'commit_dt = %s,commit_con=%s where id= %s'
    course.execute(sql, (current_branch, commit_id, author, commit_dt, commit_con, pk))
    db.commit()
    return Response({"status": 0, "data": {}})


def async_test():
    import time
    print("OK")
    time.sleep(10)
    print("time 50++++++")
    time.sleep(50)
    with open('a','w+') as f:
        f.write("111")


@bp_host.route('/code_async',methods=['get'])
def code_async():
    from flask import current_app
    # current_app.apscheduler.add_job(id="1",func=async_test,trigger='interval',seconds=2,replace_existing=True)
    current_app.apscheduler.add_job(id="1", func=async_test)
    return Response({"status":0,"data":{}})