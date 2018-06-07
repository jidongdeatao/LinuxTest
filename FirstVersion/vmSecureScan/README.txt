======================== 功能说明  ========================
作用：登陆linux服务器，扫描服务器敏感信息

windows执行说明：
1、安装执行环境
   1.1 安装python2.7与配置环境变量（此处不再赘述）
   1.2 安装pycrypto、ecdsa、setuptools、paramiko包（自行百度）
    
2、配置vmSecureScan\config\containerInfo.csv（服务器信息配置）
第1列：服务器IP
第2列：服务器名
第3列：服务器登陆账号
第4列：服务器登陆密码
第5列：服务器管理员账号（只能root）
第6列：服务器管理员密码
一个服务器配置一行哦

3、配置vmSecureScan\config\script目录下的脚本
    这些脚本将被拷贝到linux上执行，并把执行结果保存在windows本地
    可以自行删除、添加和修改脚本
    默认的脚本说明，请参看\config\script-description.txt

4、配置vmSecureScan\config\history目录下的文件
    这些文件记录了被定位为非问题的扫描结果，用来和当前扫描结果对比，使扫描结果中筛选掉非问题。
    注意：文件名称，必须与vmSecureScan\result-****目录下的扫描结果名称一模一样。文件格式见history目录下的示例。
    PS：history目录下的配置，也可以用来筛选掉已知问题，排查出新问题。如果不想筛选，清空history目录即可。

5、执行
双击run.py 或 cmd打开运行窗口，执行命令python run.py

6、结果
结果存放在vmSecureScan/result/compareResult-****
如果配置了第4步，筛选掉（认为不是问题的）存在在vmSecureScan/result/abandonResult-****


注意点说明：
    脚本使用编码格式为win7 64位默认的GBK（GB2312），如果使用其他系统，可能需要修改编码格式。
    可能要修改的地方（没试过哦，仅供参考）：
    1、run.py和scanFunctionDef.py的第一行
    2、run.py和scanFunctionDef.py用Notepad++打开，工具栏点击“格式”，选择与系统相同的编码格式。
