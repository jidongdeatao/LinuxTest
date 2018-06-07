key_words='C1oudc0w|z9a3Pa55|PaaS#|a123456|FusionSphere123|(root|admin|abc|abcd|Password|Changeme|Test|Administrator)(_12|@[^\]]|#|12|\![^\"])[^(\=|block|live|virtfs|foobar|localhost)]|([^(\^| )]@|[^(\^| |\")]#|123|[^(\^| )]\!|1234)(root|admin|abc|abcd|\.com|_com|@com)[^\.com]|(root|admin|abc|abcd)(root|admin|abc|abcd)'

dir=$(ls -l / |awk '/^d/ {print $NF}')
for i in $dir
do
    if [ $i == 'temp' ]||[ $i == 'runScan' ]||[ $i == 'proc' ]||[ $i == 'boot' ]||[ $i == 'tmp' ];then
        continue
    fi
    find /$i -type f | xargs file|grep -E 'text|XML|PC bitmap data'|awk '{print $1}'|sed 's/:$//g'|xargs grep -i -a -n -E -H "$key_words" | egrep -v 'oss3ca@huawei\.com|bash_history|Binary file|containerScan|vmSecureScan|/devicemapper/mnt' 2>/dev/null
done
