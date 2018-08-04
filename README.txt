# LinuxTest

脚本结构：
1.传入节点信息(使用python操作excel文件）
2.传入shell命令(使用python操作excel文件）
3.在vm中执行shell命令
4.保存shell执行结果到本地(使用python操作excel文件）



Linux主机本地信息自动采集工具LinEnum
copy from GItHub：
https://github.com/rebootuser/LinEnum
Example: ./LinEnum.sh -s -k keyword -r report -e /tmp/ -t
主要功能：
1.内核和发行版本
2.系统信息:
主机名
3.网络信息:
IP
路由信息
DNS服务器信息
4.用户信息:
当前用户信息
最近登录用户
枚举所有用户，包括uid/gid信息
列举root账号
检查/etc/passwd中的hash
当前用户操作记录 (i.e .bash_history, .nano_history etc.)
5.版本信息:
Sudo
MYSQL
Postgres
Apache
