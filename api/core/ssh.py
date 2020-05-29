import paramiko


class SshCommand(object):
    def __init__(self, host_name, port=22, username='root', password='*'):
        self.ssh = paramiko.SSHClient()
        self.host_name = host_name
        self.port = port
        self.username = username
        self.password = password
        self.auth_connect()
        self.exec('cd /home/pinba/app/ddd && ls')

    def auth_connect(self):
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.ssh.connect(hostname=self.host_name, port=self.port, username=self.username, password=self.password)
        except paramiko.ssh_exception.AuthenticationException:
            return False

    def exec(self, command):
        stdin, stdout, stderr = self.ssh.exec_command(command)
        res, err = stdout.read(), stderr.read()
        result = res if res else err
        res = result.decode("utf-8")
        return res

    def get_nginx(self):
        conf_dir = "/etc/nginx/conf.d/"
        files = self.exec('ls %s' % conf_dir)
        results = {}
        for f in files.split("\n"):
            if f.endswith("conf"):
                r = self.exec('cat %s%s' % (conf_dir, f))
                results[f] = r.replace("\n","\r\n")
        return results
