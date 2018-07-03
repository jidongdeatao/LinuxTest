是否执行	策略名	命令	支持扫描主体	是否安全红线(YES|NO)	说明
true	VM_fileaccess	"find / ! -perm 600 -name *.key ! -user root -exec ls -l {} \; 2>/dev/null
find / ! -perm 600 -name *.pwd ! -user root -exec ls -l {} \; 2>/dev/null
find / ! -perm 600 -name *.keytab ! -user root -exec ls -l {} \; 2>/dev/null
find / ! -perm 600 -name *.crt ! -user root -exec ls -l {} \; 2>/dev/null
find / ! -perm 600 -name *.pem ! -user root -exec ls -l {} \; 2>/dev/null
find / ! -perm 640 ! -perm 600 -name *.log ! -user root -exec ls -l {} \; 2>/dev/null
find / -type f ! -user root -perm -640 ! -perm -700 ! -perm 640 -exec ls -l {} \; 2>/dev/null | egrep -v -i '/proc/|*.log$|*.key$|*.crt$|*.pem$'
find / -type f ! -user root -perm -750 ! -perm 750 -exec ls -l {} \; 2>/dev/null | egrep -v -i '/proc/|*.log$|*.key$|*.crt$|*.pem$'
find / -type d ! -user root -perm -750 ! -perm 750 -exec ls -ld {} \; 2>/dev/null | egrep -v -i '/proc/'
find / ! -perm 600 -name *.frm -exec ls -l {} \; 2>/dev/null
find / ! -perm 600 -name *.MYI -exec ls -l {} \; 2>/dev/null
find / ! -perm 600 -name *.MYD -exec ls -l {} \; 2>/dev/null
find / ! -perm 600 -name *.ibd -exec ls -l {} \; 2>/dev/null
find / ! -perm 600 -name *ibdata* -exec ls -l {} \; 2>/dev/null"	OS,Docker	NO	"所有非root用户的文件权限：
1）含有敏感信息的文件不得大于600（rw------）对于多个OS用户都需要访问敏感文件的场景都不得大于640（rw-r-----），如：数据库备份恢复
2）日志文件不得大于640（rw-r-----）
3）不可执行文件不得大于640（rw-r-----）
4）可执行文件不得大于750（rwxr-x---）
5）目录不得大于750（rwxr-x---），有时候目录要求不能大于700（rwx------）"
true	VM_gccTools	rpm -qa | egrep -i -E '(^make|^gcc|^gcc-c++|^cpp|^gdb|^binutils|^glibc_devel|^flex|^tcpdump|^mirror|^glibc-devel|^dexdump|^toolbox|^Netcat|^Wireshark|^ethereal|strace)'	OS,Docker	NO	检查系统中不能安装调试工具：make|gcc|gcc-c++|cpp|gdb|binutils|glibc_devel|flex|tcpdump|mirror|glibc-devel|dexdump|toolbox|Netcat|Wireshark|ethereal
true	VM_nouser	find / -nouser 2>/dev/null	OS,Docker	NO	检查系统中的无属主文件
true	VM_RootProcess	ps -ef | egrep -v  '[[0-9]*]| pts/' |grep 'root '	OS,Docker	NO	检查进程越权，产品进程是否用root账号启动
true	VM_SensitiveInPross	ps -ef | egrep -i "pass|password|passwd|pswd|mima|key|pwd|PINNUMBER|secret|X-Auth-Token|Authorization|sessionID|token|email"	OS,Docker	YES	检查进程中的敏感信息，关键字："pass|password|passwd|pswd|mima|key|pwd|PINNUMBER|secret|X-Auth-Token|Authorization|sessionID|token|email"
true	VM_unSavePross	ps -ef | egrep -i "bootps|pure-ftpd|pppoe|sendmail|isdn|zebra|cupsd|cups-config-daemon|hplip|hpiod|hpssd|bluetooth|hcid|hidd|sdpd|dund|pand|rsh|telnet"	OS,Docker	NO	检查进程中是否不允许使用的服务："bootps|pure-ftpd|pppoe|sendmail|isdn|zebra|cupsd|cups-config-daemon|hplip|hpiod|hpssd|bluetooth|hcid|hidd|sdpd|dund|pand|rsh|telnet"
true	VM_systemUser	cat /etc/passwd |egrep "[0-9]{4}"	OS,Docker	NO	检查系统中是否含有不需要的账号
true	VM_systemUserPassword	cat /etc/shadow |egrep -v "(.*?:\*|.*?:\!)"	OS,Docker	YES	检查系统账号的的密码加密安全（比如不能用Base64加密）
true	VM_DBProcess	ps -ef | egrep -i 'mysql' |egrep -v "grep"	OS,Docker	YES	运行数据库进程的帐号权限应该遵循最小权限原则，要使用操作系统的非管理员权限帐号来运行数据库
true	VM_unSafeService	rpm -qa | egrep -i -E "telnet|ftp|nfs|Samba|RPC|TFTP|Netbios|X-Windows|Snmp|portmap|bluetooth"	OS,Docker	NO	检查是否安装了不安全的服务
