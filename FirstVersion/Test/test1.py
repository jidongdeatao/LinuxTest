#该脚本用于验证环境是否搭建成功
#虚机节点是否可以进行连接

import paramiko

def getSystemInfo():
    systemInfo = []

    ip = '192.145.40.52'
    systemname = 'ip1'
    user = 'funcgraph'
    password = 'FunctionGraph@#123'
    root = 'root'
    rootpassword = 'Huawei12#$'

    systemInfo.append([ip, systemname, user, password, root, rootpassword])
    return systemInfo

def run_in_vm():
    vmInfo = getSystemInfo()
    print vmInfo
    i = 0
    while i <= len(vmInfo) - 1:
        x = vmInfo[i]
        ip = x[0]
        user = x[2]
        passwd = x[3]
        rootPasswd = x[5]
        print(ip, user, passwd, rootPasswd)
        i += 1
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(ip, username=user, password=passwd)
        except:
            print(" " * 4 + "// Cannot login {ip} by \"{user}/{passwd}\". ".format(ip=ip, user=user, passwd=passwd))
        stdin, stdout, stderr = ssh.exec_command("whoami")
        curUser = stdout.read()
        ssh.close()
        return curUser


if __name__ == '__main__':
    print run_in_vm()
