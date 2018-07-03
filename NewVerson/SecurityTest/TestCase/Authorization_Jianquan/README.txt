""" 相关安全要求说明 """
所有能对系统进行管理的人机接口以及跨信任网络的机机接口必须有接入认证机制，标准协议没有认证机制的除外。
'''
'''
""" 脚本功能 """
先由开发提供角色权限信息，通过该脚本，可以对这些接口进行鉴权测试。
'''
'''
""" 脚本配置执行说明 """
配置1：/SecurityTest/Config/config.xlsx，“vmInfo”页，只需要配置一台kubectl节点虚机即可，确保该虚机能连通环境中所有其它虚机
配置2：本脚本所在目录下的RoleAuthority.xlsx，“RoleAuthority”页。每一列配置表头都有批注说明，请仔细阅读。
配置3：本脚本所在目录下的RoleAuthority.xlsx，“parameter”页。每一行配置都有说明，请仔细阅读。
'''

该脚本是通过在虚机中执行curl命令来检查接口是否满足鉴权要求

Authorization_Role.xlsx
Sheet1:RoleAuthority
界面功能	方法	接口（填写的时候请尽量填入正确参数，通用参数请填入第二页）	端口信息（格式为IP：Port)	te_admin	readonly
Sheet2:parameter
参数名	参数值	备注
te_admin_token	token值	必填项，对应前一页te_admin角色的权限（命名规则：角色名+"_token"）
readonly_token	token值	必填项，对应前一页readonly角色的权限（命名规则：角色名+"_token"）
project_id	a41bf8df857c426b97865b2cc7ed8ce4	选填项，为前一页的参数project_id赋值
