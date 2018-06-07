config.xlsx中包含两个sheet页：“vmInfo”和“otherConfig”
“vmInfo”页配置如下：
第1列：服务器IP
第2列：服务器主机名（选填，无实际用途）
第3列：服务器登陆账号
第4列：服务器登陆密码
第5列：切换服务器管理员账号（如su – root、sudo su）
第6列：服务器管理员密码
第7列：是否容器环境OM-Core节点（能够下发kubectl命令的节点）
第8列：prinvate_key，如果需要密钥登陆，则填写密钥本地完整路径，如D:/code/dis_rsa_2048（如此处不为空，脚本会判断为仅支持密钥登陆）
第9列：密钥的密码（选填，密钥没有密码的话可以不填）
注：管理面和数据面节点都请录入
	“otherConfig”页的每一项配置，在config.xlsx中自有说明
