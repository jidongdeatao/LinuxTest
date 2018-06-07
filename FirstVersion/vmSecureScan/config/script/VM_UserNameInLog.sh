key_words="\"un\":\"\w+@\""
find / -name '*.log' -type f | xargs file|grep -E 'text|XML|PC bitmap data'|awk '{print $1}'|sed 's/:$//g'|xargs grep -i -n -E -H "$key_words" |egrep -v "/devicemapper/mnt" | head -5 2>/dev/null
find / -name '*.dat' -type f | xargs file|grep -E 'text|XML|PC bitmap data'|awk '{print $1}'|sed 's/:$//g'|xargs grep -i -n -E -H "$key_words" |egrep -v "/devicemapper/mnt" | head -5 2>/dev/null
find / -name '*.trace' -type f | xargs file|grep -E 'text|XML|PC bitmap data'|awk '{print $1}'|sed 's/:$//g'|xargs grep -i -n -E -H "$key_words" |egrep -v "/devicemapper/mnt" | head -5 2>/dev/null
key_words="\"dn\":\"\w*1[0-9]{10}\""
find / -name '*.log' -type f | xargs file|grep -E 'text|XML|PC bitmap data'|awk '{print $1}'|sed 's/:$//g'|xargs grep -i -n -E -H "$key_words" |egrep -v "/devicemapper/mnt" | head -5 2>/dev/null
find / -name '*.dat' -type f | xargs file|grep -E 'text|XML|PC bitmap data'|awk '{print $1}'|sed 's/:$//g'|xargs grep -i -n -E -H "$key_words" |egrep -v "/devicemapper/mnt" | head -5 2>/dev/null
find / -name '*.trace' -type f | xargs file|grep -E 'text|XML|PC bitmap data'|awk '{print $1}'|sed 's/:$//g'|xargs grep -i -n -E -H "$key_words" |egrep -v "/devicemapper/mnt" | head -5 2>/dev/null
key_words="op_svc_sc_customer_hws"
find / -name '*.log' -type f | xargs file|grep -E 'text|XML|PC bitmap data'|awk '{print $1}'|sed 's/:$//g'|xargs grep -i -n -E -H "$key_words" |egrep -v "/devicemapper/mnt" | head -5 2>/dev/null
find / -name '*.dat' -type f | xargs file|grep -E 'text|XML|PC bitmap data'|awk '{print $1}'|sed 's/:$//g'|xargs grep -i -n -E -H "$key_words" |egrep -v "/devicemapper/mnt" | head -5 2>/dev/null
find / -name '*.trace' -type f | xargs file|grep -E 'text|XML|PC bitmap data'|awk '{print $1}'|sed 's/:$//g'|xargs grep -i -n -E -H "$key_words" |egrep -v "/devicemapper/mnt" | head -5 2>/dev/null
