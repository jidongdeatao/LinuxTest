""" 相关安全要求说明 """
《01 产品网络安全红线落地解读及指导V2_1.xls》 3.1.2 所有能对系统进行管理的人机接口以及跨信任网络的机机接口必须有接入认证机制，标准协议没有认证机制的除外。
'''
'''
""" 脚本功能 """
先由开发提供角色权限信息，通过该脚本，可以对这些接口进行鉴权测试。
'''
'''
""" 脚本配置执行说明 """
配置1：/SecurityTest/Config/config.xlsx，“vmInfo”页，只需要配置一台虚机信息即可，确保该虚机能连通环境中所有其它虚机，“是否kubectl节点”要置为TRUE
配置2：本脚本所在目录下的accessConfig.xlsx，“api”页。每一列配置表头都有批注说明，请仔细阅读。
配置3：本脚本所在目录下的accessConfig.xlsx，“parameter”页。每一行配置都有说明，请仔细阅读。
'''

accessConfig.xlsx
需配置两个Sheet页：
Sheet1：api
界面功能	操作说明	方法	接口	端口信息	head	user1_body

Sheet2：parameter
参数名	参数值	备注
user1_name	bcs01_hk	必填项，对应user1的用户名，测试账号，所有API必须在该账号下curl通
user2_name	bcs02_hk	必填项，对应user2的用户名，越权账号，在user1调通的curl命令，更换成user2的认证后，进行越权测试
user1_token	token1	必填项，对应user1用户的token
user2_token	token2	必填项，对应user2用户的token
project_id	具体的project_id	选填项，为前一页的参数project_id赋值，能替换的参数形式有三种：{project_id}、:project_id、[project_id]
