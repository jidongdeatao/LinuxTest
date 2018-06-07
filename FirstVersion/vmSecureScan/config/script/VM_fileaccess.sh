######## paas ########
find / ! -perm 600 -name *.key -user paas -exec ls -l {} \; 2>/dev/null

find / ! -perm 600 -name *.crt -user paas -exec ls -l {} \; 2>/dev/null

find / ! -perm 600 -name *.pem -user paas -exec ls -l {} \; 2>/dev/null

#find / ! -perm 600 -name *.conf -user paas -exec ls -l {} \; 2>/dev/null

#find / ! -perm 600 -name *.json -user paas -exec ls -l {} \; 2>/dev/null

#find / ! -perm 600 -name *.bat -user paas -exec ls -l {} \; 2>/dev/null

find / ! -perm 640 ! -perm 600 -name *.log -user paas -exec ls -l {} \; 2>/dev/null

find / -type f -user paas -perm -640 ! -perm -700 ! -perm 640 -exec ls -l {} \; 2>/dev/null | egrep -v -i '/proc/|*.log$|*.key$|*.crt$|*.pem$'

find / -type f -user paas -perm -750 ! -perm 750 -exec ls -l {} \; 2>/dev/null | egrep -v -i '/proc/|*.log$|*.key$|*.crt$|*.pem$'

find / -type d -user paas -perm -750 ! -perm 750 -exec ls -ld {} \; 2>/dev/null | egrep -v -i '/proc/'

######## dbuser ########
find / ! -perm 600 -name *.key -user dbuser -exec ls -l {} \; 2>/dev/null

find / ! -perm 600 -name *.crt -user dbuser -exec ls -l {} \; 2>/dev/null

find / ! -perm 600 -name *.pem -user dbuser -exec ls -l {} \; 2>/dev/null

#find / ! -perm 600 -name *.conf -user dbuser -exec ls -l {} \; 2>/dev/null

#find / ! -perm 600 -name *.json -user dbuser -exec ls -l {} \; 2>/dev/null

#find / ! -perm 600 -name *.bat -user dbuser -exec ls -l {} \; 2>/dev/null

find / ! -perm 640 ! -perm 600 -name *.log -user dbuser -exec ls -l {} \; 2>/dev/null

find / -type f -user dbuser -perm -640 ! -perm -700 ! -perm 640 -exec ls -l {} \; 2>/dev/null | egrep -v -i '/proc/|*.log$|*.key$|*.crt$|*.pem$'

find / -type f -user dbuser -perm -750 ! -perm 750 -exec ls -l {} \; 2>/dev/null | egrep -v -i '/proc/|*.log$|*.key$|*.crt$|*.pem$'

find / -type d -user dbuser -perm -750 ! -perm 750 -exec ls -ld {} \; 2>/dev/null | egrep -v -i '/proc/'

######## elb ########
find / ! -perm 600 -name *.key -user elb -exec ls -l {} \; 2>/dev/null

find / ! -perm 600 -name *.crt -user elb -exec ls -l {} \; 2>/dev/null

find / ! -perm 600 -name *.pem -user elb -exec ls -l {} \; 2>/dev/null

#find / ! -perm 600 -name *.conf -user elb -exec ls -l {} \; 2>/dev/null

#find / ! -perm 600 -name *.json -user elb -exec ls -l {} \; 2>/dev/null

#find / ! -perm 600 -name *.bat -user elb -exec ls -l {} \; 2>/dev/null

find / ! -perm 640 ! -perm 600 -name *.log -user elb -exec ls -l {} \; 2>/dev/null

find / -type f -user elb -perm -640 ! -perm -700 ! -perm 640 -exec ls -l {} \; 2>/dev/null | egrep -v -i '/proc/|*.log$|*.key$|*.crt$|*.pem$'

find / -type f -user elb -perm -750 ! -perm 750 -exec ls -l {} \; 2>/dev/null | egrep -v -i '/proc/|*.log$|*.key$|*.crt$|*.pem$'

find / -type d -user elb -perm -750 ! -perm 750 -exec ls -ld {} \; 2>/dev/null | egrep -v -i '/proc/'

######## cspexpert ########
find / ! -perm 600 -name *.key -user cspexpert -exec ls -l {} \; 2>/dev/null

find / ! -perm 600 -name *.crt -user cspexpert -exec ls -l {} \; 2>/dev/null

find / ! -perm 600 -name *.pem -user cspexpert -exec ls -l {} \; 2>/dev/null

#find / ! -perm 600 -name *.conf -user cspexpert -exec ls -l {} \; 2>/dev/null

#find / ! -perm 600 -name *.json -user cspexpert -exec ls -l {} \; 2>/dev/null

#find / ! -perm 600 -name *.bat -user cspexpert -exec ls -l {} \; 2>/dev/null

find / ! -perm 640 ! -perm 600 -name *.log -user cspexpert -exec ls -l {} \; 2>/dev/null

find / -type f -user cspexpert -perm -640 ! -perm -700 ! -perm 640 -exec ls -l {} \; 2>/dev/null | egrep -v -i '/proc/|*.log$|*.key$|*.crt$|*.pem$'

find / -type f -user cspexpert -perm -750 ! -perm 750 -exec ls -l {} \; 2>/dev/null | egrep -v -i '/proc/|*.log$|*.key$|*.crt$|*.pem$'

find / -type d -user cspexpert -perm -750 ! -perm 750 -exec ls -ld {} \; 2>/dev/null | egrep -v -i '/proc/'

######## alluser ########
find / ! -perm 600 -name *.frm -exec ls -l {} \; 2>/dev/null

find / ! -perm 600 -name *.MYI -exec ls -l {} \; 2>/dev/null

find / ! -perm 600 -name *.MYD -exec ls -l {} \; 2>/dev/null

find / ! -perm 600 -name *.ibd -exec ls -l {} \; 2>/dev/null

find / ! -perm 600 -name *ibdata* -exec ls -l {} \; 2>/dev/null
