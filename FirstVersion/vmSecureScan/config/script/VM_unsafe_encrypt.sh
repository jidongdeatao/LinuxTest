#!/bin/bash -x


key_words='\<DES\>|\<3DES\>|\<SKIPJACK\>|\<RC2\>|\<RSA\>|\<MD2\>|\<MD4\>|\<MD5\>|\<SHA1\>|\<BASE64\>'
find / \
-path /proc -prune -o \
-path /tmp -prune -o \
-path /boot -prune -o \
-type f | xargs file|grep -E 'text|XML|PC bitmap data'|awk '{print $1}'|sed 's/:$//g'|xargs grep -i -n -E -H "$key_words" | \
egrep -i -v '\s(DES|3DES|SKIPJACK|RC2|RSA|MD2|MD4|MD5|SHA1|BASE64)\s|(DES|3DES|SKIPJACK|RC2|RSA|MD2|MD4|MD5|SHA1|BASE64)[-0-9]|\-(DES|3DES|SKIPJACK|RC2|RSA|MD2|MD4|MD5|SHA1|BASE64)|\s(DES|3DES|SKIPJACK|RC2|RSA|MD2|MD4|MD5|SHA1|BASE64)$' | \
egrep -v "bash_history|Binary file|containerScan|vmSecureScan|/devicemapper/mnt" 2>/dev/null
