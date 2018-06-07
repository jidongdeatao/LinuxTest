find / \
-path /proc -prune -o \
-path /tmp -prune -o \
-path /boot -prune -o \
-type f -name "*.sh" | xargs egrep -i -n 'bash[[:blank:]]*-[a-zA-Z]*x|set[[:blank:]]*-[a-zA-Z]*x' | egrep -v "bash_history|Binary file|containerScan|vmSecureScan|/devicemapper/mnt" 2>/dev/null

find / \
-path /proc -prune -o \
-path /tmp -prune -o \
-path /boot -prune -o \
-type f -name "*.py" | xargs egrep -i -n 'bash[[:blank:]]*-[a-zA-Z]*x|set[[:blank:]]*-[a-zA-Z]*x' | egrep -v "bash_history|Binary file|containerScan|vmSecureScan|/devicemapper/mnt" 2>/dev/null
