find / \
-path /proc -prune -o \
-path /boot -prune -o \
-path /tmp -prune -o \
-type f -name "*.py" -user paas | xargs egrep -n -i '^#|^[[:blank:]]*#' | egrep -v -i -n '#![[:blank:]]*/usr/bin/env[[:blank:]]*python|#![[:blank:]]*/usr/bin/python | #![[:blank:]]*/use/bin/python|#[[:blank:]]*Load[[:blank:]]*Modules|#[[:blank:]]*-\*- coding:[[:blank:]]*utf-8 -\*-|[[:blank:]]*#end[[:blank:]]*|[[:blank:]]*#[[:blank:]]*e\.g\.|[[:blank:]]*# for CSR|#stp|#mkdir' | egrep -v 'bash_history|Binary file|containerScan|vmSecureScan|/devicemapper/mnt' 2>/dev/null
