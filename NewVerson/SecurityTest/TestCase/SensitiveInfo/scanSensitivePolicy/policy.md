是否执行	策略名	关键字（正则表达式）	文件名	OS扫描路径	OS排除路径	支持扫描主体	是否安全红线(YES|NO)	说明
true	FIND_Password	C1oudc0w|z9a3Pa55|PaaS#|a123456|iewauH|Cloud\.123|Wasd|Om68fo|Am12|89Ijn|SsMini1		/	/proc;/boot	code,OS,Docker	YES	检查系统或源码中是否含有明文密码
true	FIND_Weak_Password	(Huawei|root|admin|abc|abcd|123|1234|QAZ|xsw|cnp200|SX3000|FusionSphere|operator|Changeme|Password|\.com|_com|com|wsx|HW)(@|#|\!|_|2|)(Huawei|root|admin|abc|abcd|12|QAZ|xsw|cnp200|SX3000|operator|\.com|_com|com|wsx|HW|@|#|_|\!)|(\"1234\"|\"1234567\"|\"guest\"|\"P@ssw0rd\"|\"root\"|\"tomcat\"|\"anonymous\"|\"admin\"|\"123456\"|\"12345\"|\"HUAWEI\"|\"Hua123wei\"|\"hua123wei\"|\"huawei\"|\"password\"|\"sa\"|\"root\"|\"toor\"|\"password\"|\"change_on_install\"|\"manager\"|\"oem_temp\"|\"tiger\"|\"aqadm\"|\"dbsnmp\"|\"a123456\"|\"Administrator\"|\"Password\")		/	/proc;/boot	code,OS,Docker,Document	YES	检查系统或源码中是否含有明文的弱口令
true	FIND_Sensitive	(pass|password|passwd|pswd|mima|key|PINNUMBER|secret|Authorization|sessionID|token|email|mobile|X-Auth-Token|akey|skey|accesskey|secretkey|access_key|secret_key)|(ak|sk)[0-9a-zA-Z_\\\"\-]{0,}(:|=)(\s|)(\"|\'|)[0-9a-zA-Z]{40,}		/	/proc;/boot	code,OS,Docker	YES	"检查系统或源码中是否含有敏感信息
提醒：
a）当搜索出来的关键字的值为变量时（如key=code、password=$code等等），也需要分析变量（code）是否有风险
b）日志文件中既不能有明文，也不能有密文密码密钥信息，日志中写入密文，要做匿名化处理
c）进一步检查含有密码和敏感信息的文件，文件权限是否限制在600以内（非安全红线检查点）"
true	FIND_UnsafeEncrypt	DES|3DES|SKIPJACK|RC2|RSA|MD2|MD4|MD5|SHA1|base64|Blowfish|2TDEA|TEA|SEAL|CipherFactory|cipherName|Cipher|getInstance|SecretKeySpec|SecretKeyFactory|generateSecret|KeyFactory|IvParameterSpec|MessageDigest|PBKDF2WithHmacMD5|signature|PBKDF|PBEKeySpec|[a-zA-Z0-9]{10,}==|mac.*hash		/	/proc;/boot	code,OS,Docker	YES	"检查系统或源码中是否使用了不安全加密算法
参考：http://3ms.huawei.com/km/blogs/details/5491857
可以学习下http://3ms.huawei.com/km/blogs/details/1739153"
true	FIND_Annotation_python	^#|^\s*#|[\"]{3}|[\']{3}	.py	/	/proc;/boot	code,OS,Docker	NO	python脚本解释性语言（严禁使用注释行等形式仅使功能失效）
true	FIND_Annotation_sh	^#|^\s*#|^\s*//'	.sh	/	/proc;/boot	code,OS,Docker	NO	shell脚本解释性语言（严禁使用注释行等形式仅使功能失效）
true	FIND_Annotation_html	^\s*<\!--|^\s*//|^\s*/\*|^\s*\*	.html	/	/proc;/boot	code,OS,Docker	NO	html语言的解释性语言（严禁使用注释行等形式仅使功能失效）
true	FIND_Annotation_js	^\s*<\!--|^\s*//|^\s*/\*|^\s*\*	.js	/	/proc;/boot	code,OS,Docker	NO	js语言的解释性语言（严禁使用注释行等形式仅使功能失效）
true	FIND_DebugModel	bash\s+\-[a-zA-Z]*x|set\s+\-[a-zA-Z]*x|^#\s+set\s+\+[a-zA-Z]*x|^#\s+bash\s+\+[a-zA-Z]*x		/	/proc;/boot	code,OS,Docker	NO	"禁止使用调试模式执行shell脚本，调试模式执行shell脚本，虽然能比较方便的查看脚本执行过程以及数据信息，但也会暴露相关的数据，包括可能的敏感信息，存在被利用的风险，调试模式有两种：
a)命令行调用shell脚本时使用选项“-x”，如“bash -x test.sh”
b)在shell脚本中使用命令“set -x”打开调试模式。"
true	FIND_EncryptTool	encrypt|enc|dec|decrypt				code	NO	禁止提供独立的解密敏感数据的工具和脚本
true	FIND_EmployID	\W([a-z]00[0-9][0-9][0-9][0-9][0-9][0-9]|[a-z]wx[0-9][0-9][0-9][0-9][0-9][0-9]|[a-z]9[0-9][0-9][0-9][0-9][0-9][0-9][0-9]|[a-z]kf[0-9][0-9][0-9][0-9][0-9])\W				code	NO	排查源码中可能暴露的员工工号（重点排查shell脚本，以及其他可执行脚本，如python）
true	FIND_UserName	userid|username|user|username|usrid|user|uid|ftp|ftpuser|super|superuser|root|name|loginname|login|ftpid|101|fixation|system|sys|super|support|master|imapuser|verfiycode|authenticationcode|sharekey|sharecode|key|ftppasswd|ftppass|ftppassword|passcode|manager|privilege|sysadmin|administrator|admin				code	YES	禁止不可管理的认证/访问方式1：用户不可管理的帐号
true	FIND_Keyboard	(ctrl|alt|shift|F1)((?![0-9A-Za-z]|\s*=|\[|\.|\s*:|\||\?|\{|\(|\\).)				code	NO	禁止存在绕过正常认证机制直接进入到系统的隐秘通道1：组合键、鼠标特殊敲击
true	FIND_Injection_C&C++	system|_wsystem|popen|ShellExecute|ShellExecuteA|ShellExecuteW|WinExec|spawnve|spawnvpe|spawn|spawnlpe|spawnlp|spawnl|spawnle|spawnvp|spawnv|_spawn|_spawnlpe|_spawnlp|_spawnl|_spawnle|_wspawn|_wspawnlpe|_wspawnlp|_wspawnl|_wspawnle|_tspawn|_tspawnlpe|_tspawnlp|_tspawnl|_tspawnle|_spawnve|_spawnvpe|_wspawnve|_wspawnvpe|_tspawnve|_tspawnvpe|_spawnvp|_spawnv|_wspawnvp|_wspawnv|_tspawnvp|_tspawnv|g_spawn_command_line_async|g_spawn_command_line_sync|g_spawn_async_with_pipes|g_spawn_async|g_spawn_sync|exec|execlp|execl|execlpe|execle|execv|execvp|_exec|_execv|_execvp|_texec|_texecv|_texecvp|_wexec|_wexecv|_wexecvp|_execve|_execvpe|_texecve|_texecvpe|_wexecve|_texecvpe|_execlp|_execl|_execlpe|_execle|_texec|_texeclp|_texecl|_texeclpe|_texecle|_wexec|_wexeclp|_wexecl|_wexeclpe|_wexecle|CreateProcess|CreateProcessA|CreateProcessW|CreateProcessWithTokenW|CreateProcessAsUser|CreateProcessAsUserA|CreateProcessAsUserW|CreateProcessWithLoginW|CreateProcessWithLogonW	.c;.cpp;.h			code	NO	"C语言命令注入（Command Injection）风险：
1、（system，_wsystem）操作系统的命令解释器，如果允许用户输入命令参数，则用户可以通过命令连接符进行命令注入。
2、（popen）管道启动进程相关函数。
3、（ShellExecute，ShellExecuteA，ShellExecuteW）windows下shell相关API类似system函数，容易导致操作系统命令注入漏洞。
4、（spawn系列函数）如果将用户的输入作为spawn函数的应用程序名称参数(file)，命令行参数(argv[])或环境变量参数（envp[]），可能会导致用户随意输入程序路径执行恶意命令。
5、（exec系列函数）如果将用户的输入作为exec函数的应用程序名称参数(file或path)，命令行参数(argv[])或环境变量参数（envp[]），可能会导致用户随意输入程序路径执行恶意命令。
6、（CreateProcess系列函数）如果将用户的输入作为Windows下创建进程相关API的应用程序名称参数(lpApplicationName)或命令行参数(lpCommandLine)，可能会导致用户随意输入程序路径执行恶意命令。"
true	FIND_Injection_JAVA	\w\.exec\(|\w\.command\(|flex\.management\.jmx\.MBeanServerGateway\.invoke|flex\.messaging\.io\.amf\.client\.AMFConnection\.call|org\.apache\.axis\.client\.AdminClient\.main|org\.apache\.axis\.client\.AdminClient\.process|org\.apache\.axis\.client\.Call\.invoke|org\.apache\.axis\.client\.Call\.setOperation|org\.apache\.axis\.client\.Call\.setOperationName|org\.apache\.axis\.client\.Call\.SOAActionURI|org\.apache\.axis\.client\.Call\.setTargetEndpointAddress|org\.owasp\.esapi\.Executor\.executeSystemCommand|org\.apache\.hadoop\.util\.ProgramDriver\.driver|org\.apache\.hadoop\.util\.Tool\.run|org\.apache\.hadoop\.util\.RunJar\.main|org\.apache\.hadoop\.util\.Shell\.execCommand|org\.apache\.hadoop\.streaming\.StreamJob\.run|org\.apache\.hadoop\.mapred\.tools\.MRAdmin\.run	.java;.jsp;.js;.class			code	NO	"JAVA语言命令注入（Command Injection）风险：
1、（Runtime.exec函数）如果允许用户输入命令参数，则用户可以通过命令连接符进行命令注入。
2、（ProcessBuilder.command函数）如果将用户的输入作为ProcessBuilder.command函数的应用程序名称参数或命令行参数，可能会导致用户随意输入程序路径执行恶意命令。
3、JSP相关函数"
true	FIND_Injection_PHP	exec|shell_exec|passthru|proc_open|popen|system|ssh1_exec|ssh2_exec	.php			code	NO	"PHP语言命令注入（Command Injection）风险：
1、（exec，shell_exec，passthru，proc_open，popen，system）如果php的操作系统shell命令函数接收用户输入的命令参数，则用户可以通过命令连接符进行命令注入。
2、（ssh1_exec，ssh2_exec）远程shell命令函数，如果命令参数来自于用户的输入，则用户可以通过命令连接符，进行命令拼接，在远程主机上实施操作系统命令注入。"
true	FIND_Injection_PYTHON	subprocess\.Popen|subprocess\.call|subprocess\.check_call|subprocess\.check_output|utils\.execute|utils\.execute_with_timeout|os\.system|os\.popen|os\.popen2|os\.popen3|os\.popen4|popen2\.popen2|popen2\.popen3|popen2\.popen4|popen2\.Popen3|popen2\.Popen4|commands\.getoutput|commands\.getstatusoutput	.py;.pyc			code	NO	"PYTHON语言命令注入（Command Injection）风险：
1、（os系列命令）如果允许用户输入命令参数，则用户可以通过命令连接符进行命令注入。
2、（subprocess系列命令）如果允许用户输入命令参数，则用户可以通过命令连接符进行命令注入。
3、（utils系列命令）如果允许用户输入命令参数，则用户可以通过命令连接符进行命令注入。
4、（popen2系列命令）如果允许用户输入命令参数，则用户可以通过命令连接符进行命令注入。
5、（commands系列命令）如果允许用户输入命令参数，则用户可以通过命令连接符进行命令注入。"
true	FIND_Injection_GO	exec\.Command\(	.go			code	NO	"GO语言命令注入（Command Injection）风险：
1、（exec.Command(path,arg)）path参数启动shell执行命令时，如果允许用户输入命令参数，则用户可以通过命令连接符进行命令注入。"
true	FIND_SQL	((?![a-zA-Z0-9_\s\-]).)\s*select\s				code	NO	禁止直接使用不可信数据拼接SQL语句
true	FIND_REQUEST_URL	href\s*\=.*\$\{\w+\}|\Waction\s*\=.*\$\{\w+\}|[^-]url\s*\=.*\$\{\w+\}|\.getRequestURL\(|\.getRequestURI\(|\.startsWith\(|\.endsWith\(|\.contains\(	.java;.js;.css;.html;.jsp;.tag;.usl;.xml			code	NO	"url注入，参考：
http://3ms.huawei.com/hi/group/1503621/wiki_4439281.html
http://3ms.huawei.com/hi/group/1503621/wiki_3141499.html"
true	FIND_HTTP	http(?!(:|s|\s))				code	NO	检查源码中是否有采用http方式进行数据传输
true	FIND_Create_File	os\.Create\(|os\.MkdirAll\(	.go			code	NO	源码中创建了文件和目录，要检查是否限制了文件和目录权限
true	FIND_HAZARD_FUNCTION_C&C++	memcpy\(|wmemcpy\(|memmove\(|wmemmove\(|memset\(|strcpy\(|wcscpy\(|strncpy\(|wcsncpy\(|strcat\(|wcscat\(|strncat\(|wcsncat\(|sprintf\(|swprintf\(|vsprintf\(|vswprintf\(|snprintf\(|vsnprintf\( |scanf\(|wscanf\(|vscanf\(|vwscanf\(|fscanf\(|fwscanf\(|vfscanf\(|vfwscanf\(|sscanf\(|swscanf\(|vsscanf\(|vswscanf\(|gets\(	.c;.cpp;.h					C语言中的危险函数
true	FIND_Random_C&C++	rand\(\)|random\(\)	.c;.cpp;.h			code	NO	C标准库函数rand()和random()产生的随机数随机性很不好，其产生的随机数序列存在一个较短的循环周期，因此它的随机数是可预测的，禁止用于安全用途。
true	FIND_Random_JAVA	java\.util\.Random	.java;.jsp;.js;.class			code	NO	"java.util.Random类不能用于安全敏感应用或者敏感数据保护。应使用更加安全的随机数生成器，例如java.security.SecureRandom类。
但是java.security.SecureRandom类本身有可能会产生阻塞的情况，所以建议在非敏感应用或者非敏感数据保护时使用伪随机数生成器PRNG。"
true	FIND_Random_PHP	rnd\(	.php			code	NO	禁止使用rnd()函数生成安全随机数，安全随机数长度至少8个byte。
true	FIND_Random_PYTHON	random\.	.py;.pyc			code	NO	Python产生随机数的功能在random模块中实现，实现了各种分布的伪随机数生成器，不能应用于安全加密目的的应用中。如果你需要一个真正的密码安全随机数，在Linux和类Unix下用，请使用/dev/random生成安全随机数，在windows下，使用random模块中的SystemRandom类来实现。
true	FIND_Random_GO	rand\(|random\(	.go			code	NO	cryto/rand包中提供了密码学安全伪随机数生成器，它提供了Reader变量，在Unix系统中Reader读取/dev/urandom生成随机数、在Linux系统中Reader使用getrandom生成随机数、在Windows系统中Reader使用CryptGenRandom API生成随机数。
true	FIND_TLS_CONFIG	tls\.Config\{				code	NO	检查源码中的TLS配置（脚本中特殊处理，会打印源码中含有关键字的那一行及后面5行，方便分析）
true	FIND_PublicIP	\d+\.\d+\.\d+\.\d+				code	NO	"不需要与公网进行交互的产品/组件，IP地址使用“私网地址”，禁止使用公网地址。
说明：
默认私有地址范围：
  IPv4: 
  A类 10.0.0.0-10.255.255.255；
  B类 172.16.0.0-172.31.255.255；
  C类 192.168.0.0-192.168.255.255
  IPv6：
  fc00::/7 （Site-Local IPv6 Unicast Addresses，站点本地单播地址，相当于IPv4的私有地址）
  fe80::/10 （Link-Local IPv6 Unicast Addresses，链路本地单播地址，IPv6特有地址）"
