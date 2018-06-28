#该脚本用于验证多线程可以获取到执行结果
#从Excel中获取节点信息的方法先跳过

#!/usr/bin/python
# -*- coding: UTF-8 -*-

import paramiko
import threading
import Queue

#获取节点信息，从excel文件中获取，涉及I/O操作
def getSystemInfo():
    vmInfo = [['192.145.40.52', 'ip1', 'funcgraph', 'FunctionGraph@#123', 'root', 'Huawei12#$'],
     ['192.145.40.52', 'ip1', 'funcgraph', 'FunctionGraph@#123', 'root', 'Huawei12#$'],
     ['192.145.40.52', 'ip1', 'funcgraph', 'FunctionGraph@#123', 'root', 'Huawei12#$'],
     ['192.145.40.52', 'ip1', 'funcgraph', 'FunctionGraph@#123', 'root', 'Huawei12#$']]
    return vmInfo

#将验证过的节点队列与要执行的命令放入到程序中进行执行
def run_in_vm(L,q):
    ip = L[0]
    user = L[2]
    passwd = L[3]
    rootPasswd = L[5]
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ip, username=user, password=passwd)
    except:
        print(" " * 4 + "// Cannot login {ip} by \"{user}/{passwd}\". ".format(ip=ip, user=user, passwd=passwd))
    stdin, stdout, stderr = ssh.exec_command("netstat -tunlp")
    curUser = stdout.read()
    ssh.close()
    q.put(curUser)

def main():
    q = Queue.Queue()
    threads = []
    vmInfo = getSystemInfo()
    for i in range(len(vmInfo)):
        t = threading.Thread(target=run_in_vm,args=(vmInfo[i],q))
        t.start()
        threads.append(t)
    for thread in threads:
        thread.join()
    results = []
    for _ in range(len(vmInfo)):
        results.append([q.get(),_])
    print results

if __name__ == '__main__':
    main()
