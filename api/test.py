"""
1、全局块：配置影响nginx全局的指令。一般有运行nginx服务器的用户组，
    nginx进程pid存放路径，日志存放路径，配置文件引入，允许生成worker process数等。
2、events块：配置影响nginx服务器或与用户的网络连接。有每个进程的最大连接数，
    选取哪种事件驱动模型处理连接请求，是否允许同时接受多个网路连接，开启多个网络连接序列化等。
3、http块：可以嵌套多个server，配置代理，缓存，日志定义等绝大多数功能和第三方模块的配置。
    如文件引入，mime-type定义，日志自定义，是否使用sendfile传输文件，连接超时时间，单连接请求数等。
4、server块：配置虚拟主机的相关参数，一个http中可以有多个server。
5、location块：配置请求的路由，以及各种页面的处理情况。

"""


class NginxParser:
    def __init__(self, source=None):
        self.source = source
        self.http_block = []
        self.server_block = []
        self.location_block = []
        self.lines = []

    NOTES = ["#"]

    def init_source(self):
        """
            保证每行数据不互相影响 取消注释
        :return:
        """
        self.source = self.source.replace(";", ";\n")
        self.source = self.source.replace("{", "{\n")
        self.source = self.source.replace("}", "}\n")
        for s in self.source.split("\n"):
            _s = s.strip()
            if _s == "":
                continue
            is_note = False
            for note in self.NOTES:
                if _s.startswith(note):
                    is_note = True
                    break
            if is_note:
                continue
            self.lines.append(_s)

    def get_http(self):
        for line in self.lines:
            if line.startswith("http"):
                pass

    def get_location(self, lines=None,server_name=None):
        if lines is None: lines = self.lines
        start = 0
        fg = 0
        _f = False
        locations = []
        for index, line in enumerate(lines):
            if line.startswith("location"):
                _u = line.replace("location","")
                _u = _u.replace("{","")
                _u = _u.strip()
                _f = True
                start = index
            if _f:
                if "{" in line: fg += 1
                if "}" in line: fg -= 1

                if fg == 0:
                    end = index
                    _f = False
                    current_lines = lines[start:end]
                    if _u and server_name:
                        current_lines.append("server_name %s%s;"%(server_name,_u))
                    locations.append(current_lines)
        _locations = []
        for location in locations:
            _location = {}
            for l in location:
                if ";" in l:
                    ag = l.split()
                    if len(ag) == 2:
                        _location[ag[0]] = ag[-1].strip(";")
                    if len(ag) > 2:
                        _location["%s %s" % (ag[0], " ".join(ag[1:-1]))] = ag[-1].strip(";")
            _locations.append(_location)

        return _locations

    def get_server(self,lines = None):
        if lines is None: lines = self.lines
        start = 0
        fg = 0
        _f = False
        servers = []
        for index, line in enumerate(lines):
            if line.startswith("server"):
                _f = True
                start = index
            if _f:
                if "{" in line: fg += 1
                if "}" in line: fg -= 1

                if fg == 0:
                    end = index
                    _f = False
                    servers.append(lines[start:end])
        _servers=[]
        for server in servers:
            _server = {}
            for l in server:
                if ";" in l:
                    ag = l.split()
                    if len(ag) == 2:
                        _server[ag[0]] = ag[-1].strip(";")
                    if len(ag) > 2:
                        _server["%s %s" % (ag[0], " ".join(ag[1:-1]))] = ag[-1].strip(";")
            _server["location"] = self.get_location(server,server_name=_server.get("server_name"))
            _servers.append(_server)
        return _servers
    def load(self, source):
        self.source = source

    def as_json(self):
        self.init_source()
        return self.get_server()

    def parser_website(self):
        """
            解析站点配置
        :return:
        """
        servers = self.as_json()
        website = []
        for server in servers:
            server_name = server.get("server_name")
            root = server.get("root")
            alias = server.get("alias")
            proxy_pass = server.get("proxy_pass")
            if server_name and (root or alias or proxy_pass):
                website[server_name] = root or alias or proxy_pass
            for loc in server.get("location",[]):
                server_name = loc.get("server_name")
                root = loc.get("root")
                alias = loc.get("alias")
                proxy_pass = loc.get("proxy_pass")
                if server_name and (root or alias or proxy_pass):
                    website.append({
                        "server_name":server_name,
                        "proxy":root or alias or proxy_pass
                    })
        return website

