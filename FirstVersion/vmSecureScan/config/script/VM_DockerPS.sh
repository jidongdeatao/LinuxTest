images=(`docker ps |egrep -v "pause|CONTAINER" |awk '{print $2}'`)
docker=(`docker ps |egrep -v "pause|CONTAINER" |awk '{print $1}'`)
mounts=(`find / -name "mount-id"`)

i=0
len=${#docker[@]}
len_mount=${#mounts[@]}
while(($i<$len))
do
	echo "############### containerID: ${docker[$i]};   image: ${images[$i]}"
	j=0
	while(($j<$len_mount))
	do
		x=`echo "${mounts[$j]}" |grep ${docker[$i]}`
		if [ -n "$x" ];then
			mntID=`cat ${mounts[$j]}`
			echo mntID: $mntID
		fi
		j=$(($j+1))
	done
	echo ""
	i=$(($i+1))
done
