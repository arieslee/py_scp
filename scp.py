#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2020/5/20 10:34 AM
# @Author  : Aries (i@iw3c.com)
# @Site    : http://iw3c.com
# @File    : scp.py
# @Software: PyCharm
import paramiko,sys,io,time

ip = ''
pwd = ''
user = ''
port = 0
remote_file = ''
local_file = ''

def scp_upload(ip,port,user,pwd,local_file,remote_file):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, port, user, pwd)
    a = ssh.exec_command('date')
    stdin, stdout, stderr = a
    print(stdout.read())
    sftp = paramiko.SFTPClient.from_transport(ssh.get_transport())
    sftp_connect = ssh.open_sftp()
    sftp_connect.put(local_file, remote_file)
    print("文件"+local_file+"上传完成，上传路径为："+remote_file)

def scp_download(ip,port,user,pwd,remote_file,local_file):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, port, user, pwd)
    a = ssh.exec_command('date')
    stdin, stdout, stderr = a
    print(stdout.read())
    sftp = paramiko.SFTPClient.from_transport(ssh.get_transport())
    sftp_connect = ssh.open_sftp()
    sftp_connect.get(remote_file, local_file)

def get_input_params():
    global ip, port, user, pwd, remote_file, local_file
    ip = input("请输入远端主机的IP地址：")
    port = input("请输入端口：")
    user = input("请输入登录账号：")
    pwd = input("请输入登录密码：")
    remote_file = input("请输入远程文件的保存路径：")
    local_file = input("请输入本地文件的路径：")
    verify_input()

def verify_input():
    print(ip)
    if ip.strip() == '':
        print("请输入ip")
        exit()
    if port == 0:
        print("请输入端口")
        exit()
    if user.strip() == '':
        print("请输入登录账号")
        exit()
    if pwd.strip() == '':
        print("请输入登录密码")
        exit()
    if remote_file.strip() == '':
        print("请输入远程文件保存路径")
        exit()
    if local_file.strip() == '':
        print("请输入本地文件路径")
        exit()

def receive_input():
    print ('''
    -------欢迎使用 scp software--------
     请老几scp命令的格式：scp -P 29999 local_path/go.tar.gz username@serverip:server_path
     上传文件请输入  [ 1 ]:
     下载文件请输入  [ 2 ]:
     退出SCP请输入   [ q ]:
------------------------------------
    ''')
    choice = input("请输入 [ ]")
    if choice == '1':
        get_input_params()
        scp_upload(ip,port,user,pwd,local_file,remote_file)
    elif choice == '2':
        get_input_params()
        scp_download(ip,port,user,pwd,remote_file,local_file)
    elif choice == 'q':
        print("感谢使用^_^")
        exit()
    else:
        print("输入错误")

if __name__ == '__main__':
    while True :
        receive_input()