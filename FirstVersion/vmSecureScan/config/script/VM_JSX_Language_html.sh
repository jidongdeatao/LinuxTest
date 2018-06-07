find / \
-path /proc -prune -o \
-path /boot -prune -o \
-path /tmp -prune -o \
-type f -name "*.html" -user paas | xargs egrep -n -i '^[[:blank:]]*<\!--|^[[:blank:]]*//|^[[:blank:]]*/\*' | egrep -v 'bash_history|Binary file|containerScan|vmSecureScan|/devicemapper/mnt' 2>/dev/null
