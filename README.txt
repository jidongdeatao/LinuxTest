# LinuxTest

脚本结构：
1.传入节点信息(使用python操作excel文件）
2.传入shell命令(使用python操作excel文件）
3.在vm中执行shell命令
4.保存shell执行结果到本地(使用python操作excel文件）


共分为两个版本架构
第一个版本架构是通过直接传人shell脚本命令来获得执行结果
第二个版本增加了Excel文件控制模块，将shell命令保存到Excel文件中，达到了数据驱动框架的效果。
    仅通过维护Excel文件即可。
