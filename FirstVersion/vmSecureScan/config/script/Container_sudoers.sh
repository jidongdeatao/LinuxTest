images=(`docker ps |egrep -v "pause|CONTAINER" |awk '{print $2}'`)
docker=(`docker ps |egrep -v "pause|CONTAINER" |awk '{print $1}'`)
i=0
len=${#docker[@]}
while(($i<$len))
do
	echo "############### ${docker[$i]}  ${images[$i]}"
	docker exec -u 0 ${docker[$i]} cat /etc/sudoers |egrep -v "^#|^Defaults|^$"
	echo ""
	i=$(($i+1))
done
