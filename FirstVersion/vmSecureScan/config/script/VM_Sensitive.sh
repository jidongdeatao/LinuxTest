str1="^.*:[0-9]+:\s*(\-|\w+|)(\.|)\s*(\"|\'|)[0-9a-zA-Z_\s\-]+(\"|\'|)(\s*:|\s*=|\"\s*(:|=)|\'\s*(:|=))\s*(\{|\"|\'){0,3}(|[a-z_\.\/\-]+|0x[0-9a-zA-Z]+){0,1}(\{|\"|\'){0,3}(,|\.|)\s*(\/\/[a-zA-Z0-9\. ]+|)\W*$"
str2="^.*:[0-9]+:\s*[a-z_\/\-]+:\s*\{([a-z_\/\-]+:\s*[a-z_\/\-]+\s*,\s*|[a-z_\/\-]+:\s*[0-9_\/\-]+\s*,\s*){0,}[a-z_\/\-]+:\s*[a-z_\/\-]+\s*(\}|,)\s*\W*$"
str3="^.*:[0-9]+:\s*(\"){0,1}[a-z_\/\s\-]+(\"){0,1}\s*(=|:)\s*((\"){0,1}[a-z_\/\.\-]+(\"){0,1}(\"){0,1}|(\"){0,1}[a-z_\/\.\-]+(\"){0,1}|(\"){0,1}[A-Z_\/\.\-]+(\"){0,1})\W*$"
str4="^.*:[0-9]+:\s*(\"){0,}[a-z_\/\-]+(\"){0,}:\s*(\"){0,}\{(\\\"[a-z_\/\-]+\\\":\s*\\\"[a-z_\/\-]+\\\"\s*,\s*|\\\"[a-z_\/\-]+\\\":\s*\\\"\/[a-z0-9_\/\-]+\\\"\s*,\s*){0,}\\\"id\\\":\\\"[0-9a-zA-Z\-]+\\\"\}\"(,|)\W*$"
str5="^/opt/paas/dockyard/tarsum/[0-9a-z]+/layer:[0-9]+:\s*\{.*\}\W*$"
str6="^.*:[0-9]+:\{\"traceId\":[0-9]+,\"name\":\"([A-Za-z0-9_\/\.\-]+:){0,5}[a-z0-9_\/\.\{\}\?\=\-]+\",\"id\":[0-9\-]+,\"parentId\":[0-9\-]+,\"annotations\":\[((|\[)\{\"timestamp\":[0-9]+,\"value\":\"\w+\",\"host\":\{\"ip\":(null|\"[a-z0-9\.\-]+\"),\"port\":\"[0-9]+\"\}\}(,|\])){1,3},\"append\":(|\[)(\{\"key\":\"[a-zA-Z]+\",\"value\":\"([0-9]+|[A-Z]+|[A-Za-z\/]+|)\",\"annotationType\":\"([a-z0-9]+|[A-Z]+)\"\}(,|\])){1,10},\"extinfo\":((\"|)[a-z0-9A-Z\._\-]+(\"|)|\[\{\"key\":\"[a-zA-Z]+\",\"value\":\".*\",\"annotationType\":\"([a-z0-9]+|[A-Z]+)\"\}\])\}\W*$"
str7="^.*:[0-9]+:\{\"annotations\":((|\[)\{\"host\":\{(\"ip\":\"[a-z0-9\.\-]+\",){0,1}\"port\":\"[0-9]+\"\},\"timestamp\":[0-9]+,\"value\":\"\w+\"\}(,|\])){1,3},\"append\":((|\[)\{\"annotationType\":\"([a-z0-9]+|[A-Z]+)\",\"key\":\"[a-zA-Z]+\",\"value\":\"([0-9\-]+|[A-Z]+|[A-Za-z ]+(@[A-Za-z ]+|)|[A-Za-z ]+(\/[A-Za-z ]+|)|)\"\}(,|\]|)){1,10},(\"extinfo\":\[\{\"annotationType\":\"([a-z0-9]+|[A-Z]+)\",\"key\":\"[a-zA-Z]+\",\"value\":\".*\"\}\],){0,1}\"id\":[0-9\-]+,\"name\":\".*\",\"parentId\":[0-9\-]+,\"traceId\":[0-9\-]+\}\W*$"
str8="^.*:[0-9]+:\{\"uid\":\"([0-9a-z]+|)\",\"un\":\"([a-zA-Z0-9_]+|)\",\"ter\":\"([0-9\.:]+|)\",\"op\":\"([a-zA-Z ]+|)\",\"opl\":\"([a-zA-Z]+|)\",\"did\":\"([0-9a-z]+|)\",\"dn\":\"([a-zA-Z0-9_]+|)\",\"pid\":\"([0-9a-z]+|)\",\"pn\":\"([a-zA-Z0-9_]+|)\",\"evnt\":\"([a-zA-Z]+|)\",\"tobj\":\"([a-zA-Z0-9_]+|)\",\"res\":\"([a-zA-Z0-9_]+|)\",\"dtl\":\".*\(using password: YES\).*\",\"src\":\"([a-zA-Z0-9_\-]+|)\",\"ts\":[0-9]+(,\"indexts\":[0-9]+){0,1}\}\W*$"
str9="^.*:[0-9]+:type\=[A-Z]+\s+msg\=audit\([0-9:\.]+\)\:\s+arch\=[a-z0-9\-]+\s+syscall\=[a-z0-9\-]+\s+success\=[a-z0-9\-]+\s+exit=[a-z0-9\-]+\s+(a[0-9]+\=[a-z0-9]+\s+){1,5}items\=[a-z0-9\-]+\s+ppid\=[0-9]+\s+pid\=[0-9]+\s+auid\=[0-9]+\s+uid\=[0-9]+\s+gid\=[0-9]+\s+euid\=[0-9]+\s+suid\=[0-9]+\s+fsuid\=[0-9]+\s+egid\=[0-9]+\s+sgid\=[0-9]+\s+fsgid\=[0-9]+\s+tty\=\(none\)\s+ses\=[0-9]+\s+comm\=(\"|)[a-zA-Z0-9_\.\-]+(\"|)\s+exe\=\"[a-z0-9_\/\-]+\"\s+subj\=([a-z0-9_:\.\-]+){1,5}\s+key\=\(null\)\W*$"
str10="^.*:[0-9]+:type\=[A-Z]+\s+msg\=audit\([0-9:\.]+\)\:\s+avc:\s+denied\s+\{[a-z ]+\}\s+for\s+pid\=[0-9]+\s+comm\=\"[a-z0-9_\.\-]+\"\s+name\=\"[a-zA-Z0-9_\-]+\"\s+dev\=\"[a-zA-Z0-9_\-]+\"\s+ino\=[0-9]+\s+scontext\=([a-z0-9_:\.\-]+){1,5}\s+tcontext\=([a-z0-9_:\.\-]+){1,5}\s+tclass\=[a-z0-9_:\.\-]+\W*$"
str11="^.*oss\.zookeeper\.log:[0-9]+:[0-9:\s\-]+,[0-9]+\s+INFO\s+\(ProcessThread\([a-z0-9:\s\-]+\):\)\s+[a-zA-Z\s\-]+\s+sessionid:\s*0x(\*){6,}[a-z0-9]+\s+(type:[a-zA-Z]+\s+cxid:(0x|)[0-9a-z]+\s+zxid:(0x|)[0-9a-z]+\s+txntype:(\-|)[0-9]+\s+reqpath:[a-z\/]+\s+Error Path:[a-zA-Z0-9_\/\-]+\s+Error:KeeperErrorCode = BadVersion for [a-zA-Z0-9_\/\-]+\s+|)\(PrepRequestProcessor:[0-9]+\)\s*\W*$"
str12="^.*:[0-9]+:\s*Public\-Key:\s+\([0-9]+ bit\)\s*\W*$"
str13="^.*kubelet\.log.*:[0-9]+:[A-Z0-9]+\s+[0-9]+:[0-9]+:[0-9]+\.[0-9]+\s+[0-9]+\s+[a-zA-Z0-9]+\.go:[0-9]+\]\s+[a-zA-Z0-9_\/\.]+:[0-9]+:\s+[A-Za-z\*\. ]+:\s+[a-zA-Z0-9_\/\.\?\= :]+\W*$"
str14="^.*:[0-9]+:[0-9]{4}\-[0-9]{1,2}\-[0-9]{1,2}\s+[0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}\s+[0-9]+\s+\[[a-zA-Z]+\]\s+Access denied for user '[a-z]+'@'[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+'\s+\(using password:\s+(YES|NO)\)$"
str15="^.*/var/log/[a-zA-Z0-9\-]+:[0-9]+:.*$"

big_str1="^.*\.yaml:[0-9]+:\s*(tls.key:|tls.key.pwd:|kubeconfig:)\s*[0-9a-zA-Z]{64,}\W*$"
big_str2="^.*febsdb.*\.aof:[0-9]+:.*\"ResetPlatformAdminPwd\":\{.*$"
big_str3="^[a-zA-Z0-9_\/\-]+oss\.dbacl_tool\.trace:[0-9]+:.*\"entity\":\[(\{.*,\"total_keys\":\"[0-9]+\"\}(,|\])){1,100}.*,\"detail\":null\}\W*$"

sys_str1="^.*\/\.bash_history:[0-9]+:.*$"
sys_str2="^.*\/usr/lib(64|)\/python2\.7.*$"
sys_str3="^.*\/usr\/lib\/udev\/hwdb\.d\/[0-9]+\-keyboard\.hwdb.*$"

key_words="(pass|password|passwd|pswd|mima|key|pwd|PINNUMBER|secret|crypto|encrypt|decrypt|Authorization|sessionID|token|email|mobile)[0-9a-zA-Z_-]*(\s*:|\s*=|\"\s*(:|=)|\'\s*(:|=))|X-Auth-Token|(ak|sk|akey|skey|accesskey|secretkey|access_key|secret_key)[0-9a-zA-Z_\\\"\-]{0,}(:|=)(\s|)(\"|\'|)[0-9a-zA-Z]{40,}"
find / \
-path /proc -prune -o \
-path /boot -prune -o \
-path /tmp -prune -o \
-type f ! -name "*.bin" | xargs file|egrep -E 'text|XML|PC bitmap data'|awk '{print $1}'|sed 's/:$//g'|xargs grep -i -a -n -E -H "$key_words" \
|egrep -i -v "bash_history|Binary file|containerScan|vmSecureScan|/devicemapper/mnt|$str1|$str2|$str3|$str4|$str5|$str6|$str7|$str8|$str9|$str10|$str11|$str12|$str13|$str14|$str15|$big_str1|$big_str2|$big_str3|$sys_str1|$sys_str2|$sys_str3" 2>/dev/null
