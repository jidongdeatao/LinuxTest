

《01 产品网络安全红线落地解读及指导V2_1.xls》 3.1.2 所有能对系统进行管理的人机接口以及跨信任网络的机机接口必须有接入认证机制，标准协议没有认证机制的除外。
'''
'''
""" 脚本功能 """
先由开发或工具获取到代码中的接口信息，通过该脚本，可以对这些接口进行认证测试。
'''
'''
""" 脚本配置执行说明 """
配置1：/SecurityTest/Config/config.xlsx，“vmInfo”页
        1\
配置2：本脚本所在目录下的APIs.xlsx，“API”页。每一列配置表头都有批注说明，请仔细阅读。
配置3：本脚本所在目录下的APIs.xlsx，“parameter”页。每一行配置都有说明，请仔细阅读。

APIs.xlsx，“API”页
URI	Method	PORT	Protocol	Microservice	Parameter	Header	Class	Function	OperationId	Description
APIs.xlsx，“parameter”页
key	value	说明
certMethod		【需要做证书认证时填写，否则留空】证书认证使用的证书(注意横杠“-”开头要有空格，否则会变成运算)；使用方式见\SecurityTest\Doc目录下的《接口认证测试方法（简化版）.docx》
tokenMethod		【需要做TOKEN认证时填写，否则留空】TOKEN认证使用的token值；使用方式见\SecurityTest\Doc目录下的《接口认证测试方法（简化版）.docx》
akskMethod		【需要做AKSK认证时填写，否则留空】AKSK认证使用的AKSK值；使用方式见\SecurityTest\Doc目录下的《接口认证测试方法（简化版）.docx》
KUBERNETES_MASTER		【需要查询业务实例信息时填写，否则留空】用于设置kubectl命令环境变量KUBERNETES_MASTER的值；非容器化环境可以不用填写
sessionMethod		【需要做session认证时填写，否则留空】session认证使用的session值(注意横杠“-”开头要有空格，否则会变成运算)；使用方式见\SecurityTest\Doc目录下的《接口认证测试方法（简化版）.docx》
sessionPort		【需要做session认证时填写，否则留空】cookie认证所在IP和端口，格式为IP:PORT
project_id		【"API页签"具体的API参数】"API页签"具体的API 业务变参，可根据业务实际动态往下增加



测试结果说明：
认证
Pass:接口做了认证，测试结果通过
Fail:接口未作认证，测试结果失败
ERROR:含有认证的curl命令下发失败，可能不支持该认证方式或接口不存在，请检查
MSG_ERROR:含有认证的curl命令下发失败，直接用无认证的curl命令进行测试，测试结果需要人工判断
