#-*- coding: utf-8 -*-

import sys
import os
import re
reload(sys)
sys.setdefaultencoding('utf-8')

import LocalOperate
import LinuxOperate
import Log
g_Local = None
g_linux = None
g_Log = None
class Container:
    def __init__(self,ip=None,user=None,password=None,suRoot=None,rootPassword=None,image="ALL"):
        global g_linux,g_Local,g_Log
        g_linux = LinuxOperate.Linux(ip=ip,user=user,password=password,suRoot=suRoot,rootPassword=rootPassword)
        g_Local = LocalOperate.Local()
        g_Log = Log.Log()
        self.ip = ip
        self.user = user
        self.password = password
        self.suRoot = suRoot
        self.rootPassword = rootPassword
        self.image = image
        self.dockerInfo = self.getDockerInfo()
        self.containerInfo = None

    def Container_Mount_link(self):
        try:
            g_Log.writeLog(u"在{ip}上查询容器的docker信息和mount信息：".format(ip=self.ip))
            containerInfo = []

            mountInfo = []
            output = g_linux.sendRootCommand("find / -name mount-id")
            mounts = output[0].split("\n")
            for mount in mounts:
                x0 = g_linux.sendRootCommand("cat {file}".format(file=mount))
                mountID = x0[0].split("\n")[0]
                if mountID == "":
                    continue
                mountInfo.append([mount,mountID])

            dockerInfo = self.dockerInfo

            for docker in dockerInfo:
                for mount in mountInfo:
                    if docker[1] in mount[0]:
                        x1 = g_linux.sendRootCommand("find / -name {mountID}".format(mountID=mount[1]))
                        dirs = x1[0].split("\n")
                        for dir in dirs:
                            if "/devicemapper/mnt/" not in dir:
                                continue
                            mountLink = dir+"/rootfs"
                        containerInfo.append([docker[0],docker[1],mountLink])
            self.containerInfo = containerInfo
        except:
            g_Log.writeLog("traceback")
            return 0
        return containerInfo

    def getDockerInfo(self):
        try:
            g_Log.writeLog(u"在{ip}上查询容器的docker信息：".format(ip=self.ip))
            dockerInfo = []
            output = g_linux.sendRootCommand("docker ps |egrep -v 'CONTAINER ID|pause'")
            dockers = output[0].split("\n")
            for docker in dockers:
                if docker == "":
                    continue
                dockerID = docker.split()[0]
                dockerImage = docker.split()[1]
                dockerNames = docker.split()[-1]
                x0 = re.findall("^[a-z0-9]+$",dockerImage)
                x1 = re.findall("k8s_([a-zA-Z0-9_\.]+\-[a-zA-Z0-9\.\-]+)_",dockerNames)
                if x0!=[] and x1!=[]:
                    dockerImage = x1[0]
                dockerInfo.append([dockerImage,dockerID])
            if dockerInfo == []:
                g_Log.writeLog(u"在虚机{ip}上没有找到需要的容器:\n{docker}".format(ip=self.ip,docker=output[0]))
                return 0
        except:
            g_Log.writeLog("traceback")
            return 0
        return dockerInfo

    def getContainerID(self,image):
        try:
            g_Log.writeLog(u"在{ip}上查询容器的docker信息：".format(ip=self.ip))
            id = []
            dockerInfo = self.dockerInfo
            for docker in dockerInfo:
                if image in docker[0]:
                    id.append(docker[1])
            if id == []:
                g_Log.writeLog(u"在虚机{ip}上没有找到名为{image}的容器".format(ip=self.ip,image=image))
                return 0
        except:
            g_Log.writeLog("traceback")
            return 0
        return id

    def sendCommand(self,cmd):
        try:
            result = []
            cmd = cmd.replace("\'","\"").replace("'","\"")
            dockerInfo = self.dockerInfo
            for docker in dockerInfo:
                try:
                    g_Log.writeLog(u"[IP={ip},DockerImage={image},DockerID={id}]上正在执行命令：{cmd}".format(ip=self.ip,image=docker[0],id=docker[1],cmd=cmd))
                    output = g_linux.sendRootCommand("docker exec -u 0 {id} {cmd}".format(id=docker[1],cmd=cmd))
                    result.append(["[IP={ip},DockerImage={image},DockerID={id}]".format(ip=self.ip,image=docker[0],id=docker[1]),output[0]])
                except:
                    g_Log.writeLog("traceback")
        except:
            g_Log.writeLog("traceback")
            return 0
        return result

    def uploadFileFromLocal(self,localFile,destFile):
        try:
            localFile=localFile.replace("\\","/")
            destFile=destFile.replace("\\","/")
            fileName = localFile.split("/")[-1]
            tempFile = "/tmp/"+fileName
            g_linux.uploadFileByRead(localFile=localFile,destFile=tempFile)
            containerInfo = self.containerInfo
            if containerInfo is None:
                containerInfo = self.Container_Mount_link()
            for container in containerInfo:#[docker[0],docker[1],mountLink]
                try:
                    g_Log.writeLog(u"正在向[IP={ip},DockerImage={image},DockerID={id}]拷贝文件{file}".format(ip=self.ip,image=container[0],id=container[1],file=localFile))
                    destFile = container[2]+destFile
                    destDir = os.path.dirname(destFile)
                    output = self.sendRootCommand( "if [ -d \"{file}\" ]; then echo \"true\"; else echo \"false\"; fi".format(file=destDir) )
                    if "true" not in output[0]:
                        g_Log.writeLog(u"目的目录不存在：{file}".format(file=destDir))
                        continue
                    output = self.sendRootCommand( "ls -l {file}".format(file=destFile) )
                    if "No such file or directory" not in output[1] or "total" in output[0]:
                        g_Log.writeLog(u"目的文件已经存在：{file}".format(file=destFile))
                        continue
                    output = g_linux.sendRootCommand("cp {localFile} {destFile}".format(localFile=tempFile,destFile=destFile))
                    if output[1] != "" and len(output[1])>9:
                        continue
                    output = g_linux.sendRootCommand("ls -l {destFile}".format(destFile=destFile))
                    if output[1] != "" and len(output[1])>9:
                        continue
                except:
                    g_Log.writeLog("traceback")
            output = g_linux.sendRootCommand("rm -rf {localFile}".format(localFile=tempFile))
            output = g_linux.sendRootCommand("rm -rf {localFile}".format(localFile=tempFile))
        except:
            g_Log.writeLog("traceback")
            return 0
        return 1

    def deleteFile(self,file=None):
        try:
            containerInfo = self.containerInfo
            if containerInfo is None:
                containerInfo = self.Container_Mount_link()
                self.containerInfo = containerInfo
            for container in containerInfo:#[docker[0],docker[1],mountLink]
                try:
                    g_Log.writeLog(u"正在向[IP={ip},DockerImage={image},DockerID={id}]删除文件{file}".format(ip=self.ip,image=container[0],id=container[1],file=file))
                    output = g_linux.sendRootCommand("rm -rf {file}".format(file=file))
                    if output[1] != "" and len(output[1])>9:
                        continue
                    output = g_linux.sendRootCommand("ls -l {file}".format(file=file))
                    if output[1] != "" and len(output[1])>9:
                        continue
                except:
                    g_Log.writeLog("traceback")
        except:
            g_Log.writeLog("traceback")
            return 0
        return 1



    def logout(self):
        try:
            g_Log.writeLog(u"用户{user}/{password}注销登陆{ip}".format(user=self.user,password=self.password,ip=self.ip))
            g_linux.logout()
        except:
            g_Log.writeLog("traceback")
            return 0
        return 1








