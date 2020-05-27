import copy
import sys
from io import BytesIO

import paramiko

# 创建SSH对象
ssh = paramiko.SSHClient()
# 允许连接不在know_hosts文件中的主机
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# 连接服务器
try:
    ssh.connect(hostname='119.23.175.115', port=22, username='root', password='uhoo!@#^%$')
except paramiko.ssh_exception.AuthenticationException:
    print("认证失败")
    exit()

# 执行命令
stdin, stdout, stderr = ssh.exec_command('ls /etc/nginx/conf.d')
# 获取命令结果

result = stdout.readlines()

# 关闭连接
# print(r)
ssh.close()
for i in result:
    print("---",i.strip())

