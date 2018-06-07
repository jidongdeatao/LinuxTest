find / \
-path /proc -prune -o \
-path /boot -prune -o \
-path /tmp -prune -o \
-type f -name "*.sh" -user paas | xargs egrep -n -i '^#|^[[:blank:]]*#|^#|^[[:blank:]]*//' | egrep -v -i -n '#![[:blank:]]*/bin/bash|# source env|#!/usr/bin/env[[:blank:]]*bash|[[:blank:]]*#--*|#[[:blank:]]*create|#for euler os|#for ubuntu os|#[[:blank:]]*\/' | egrep -v 'bash_history|Binary file|containerScan|vmSecureScan|/devicemapper/mnt' 2>/dev/null
