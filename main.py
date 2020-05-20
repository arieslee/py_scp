#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2020/5/20 11:44 AM
# @Author  : Aries (i@iw3c.com)
# @Site    : http://iw3c.com
# @File    : main.py
# @Software: PyCharm
import sys
import os
from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QFileDialog,
                             QPushButton, QApplication, QMessageBox, QProgressBar, QComboBox, QRadioButton)
from PyQt5 import QtCore
import paramiko
import re
import json


class ScpUpload(QWidget):
    def __init__(self):
        super().__init__()
        self.timer = QtCore.QBasicTimer()
        self.step = 0
        self.local_file_size = 0
        self.local_file_basename = ""
        print(os.getcwd())
        self.local_account_info_db = os.getcwd()+"/info.db"
        self.account_info = {
            "ip":"",
            "port":"",
            "user":"",
            "pwd":"",
            "remote_file":"",
        }
        self.auth_type = "pwd"
        self.auth_type_pwd = QRadioButton(self)
        self.auth_type_key = QRadioButton(self)
        self.user_key_ipt = QLineEdit(self)
        self.user_key_btn = QPushButton(self)
        self.rem_file_input = QLineEdit(self)
        self.ip_input = QLineEdit(self)
        self.port_input = QLineEdit(self)
        self.user_input = QLineEdit(self)
        self.pwd_input = QLineEdit(self)
        self.local_file_ipt = QLineEdit(self)
        self.progress_bar = QProgressBar(self)

        self.init_ui()

    def open_db_file(self):
        if os.path.isfile(self.local_account_info_db):
            file_handle = open(self.local_account_info_db, 'r', encoding='utf-8')
            return file_handle
        return False

    def get_local_account_info(self):
        file_handle = self.open_db_file()
        if not file_handle:
            return False

        data = file_handle.read()
        file_handle.close()
        self.account_info = json.loads(data)

    def set_local_account_info(self):
        file_handle = open(self.local_account_info_db, 'w+', encoding='utf-8')
        if not file_handle:
            return False
        data = {
            "ip": self.ip_input.text().strip(),
            "port": self.port_input.text().strip(),
            "user": self.user_input.text().strip(),
            "pwd": self.pwd_input.text().strip(),
            "remote_file": self.rem_file_input.text().strip(),
            "auth_type": self.auth_type,
        }
        json_str = json.dumps(data)
        file_handle.write(json_str)
        file_handle.close()

    def draw_ip_input(self):
        ip_label = QLabel('服务器 IP 地址:', self)
        ip_label.setGeometry(QtCore.QRect(10, 5, 130, 45))
        self.ip_input.setGeometry(QtCore.QRect(130, 15, 180, 20))
        self.ip_input.setText(self.account_info["ip"])

    def draw_port_input(self):
        port_label = QLabel('服务器端口:', self)
        port_label.setGeometry(QtCore.QRect(10, 46, 130, 45))
        self.port_input.setGeometry(QtCore.QRect(130, 60, 180, 20))
        self.port_input.setText(self.account_info["port"])

    def draw_auth_type(self):
        label = QLabel('登录验证方式:', self)
        label.setGeometry(QtCore.QRect(10, 90, 130, 45))
        self.auth_type_key.setText("密钥")
        self.auth_type_pwd.setText("账号/密码")
        self.auth_type_pwd.setChecked(True)
        self.auth_type_pwd.move(126, 100)
        self.auth_type_key.move(230, 100)
        self.auth_type_pwd.toggled.connect(self.on_radio_button_toggled)

    def on_radio_button_toggled(self):
        if self.auth_type_pwd.isChecked():
            print("is pwd type")
        elif self.auth_type_key.isChecked():
            print("is user key type")

    def draw_user_input(self):
        user_label = QLabel('登录账号:', self)
        user_label.setGeometry(QtCore.QRect(10, 135, 130, 45))
        self.user_input.setGeometry(QtCore.QRect(130, 150, 180, 20))
        self.user_input.setText(self.account_info["user"])

    def draw_pwd_input(self):
        pwd_label = QLabel('登录密码:', self)
        pwd_label.setGeometry(QtCore.QRect(10, 175, 130, 45))
        self.pwd_input.setGeometry(QtCore.QRect(130, 190, 180, 20))
        self.pwd_input.setEchoMode(QLineEdit.Password)
        self.pwd_input.setText(self.account_info["pwd"])

    def draw_local_input(self):
        local_file_label = QLabel("本地文件路径：", self)
        local_file_label.setGeometry(QtCore.QRect(10, 215, 130, 45))
        self.local_file_ipt.setGeometry(QtCore.QRect(130, 230, 180, 20))
        btn = QPushButton("选择文件", self)
        btn.resize(btn.sizeHint())
        btn.move(305, 183)
        btn.clicked.connect(self.select_file)
        return local_file_label

    def draw_remote_input(self):
        rem_file_label = QLabel('远程文件保存路径:', self)
        rem_file_label.setGeometry(QtCore.QRect(10, 255, 130, 45))
        self.rem_file_input.setGeometry(QtCore.QRect(130, 265, 180, 20))
        self.rem_file_input.setText(self.account_info["remote_file"])

    def select_file(self):
        selected_file, file_type = QFileDialog.getOpenFileName(self,
                                                                "选取文件",
                                                                os.getcwd(),  # 起始路径
                                                                "All Files (*);;Text Files (*.txt)"
                                                                )  # 设置文件扩展名过滤,用双分号间隔

        if selected_file == "":
            print("\n取消选择")
            return

        print("\n你选择的文件为:")
        print(selected_file)
        print("文件筛选器类型: ", file_type)
        #获取文件大小
        self.local_file_size = os.path.getsize(selected_file)
        if self.local_file_size <= 0 :
            self.alert("选择的文件太小啦")
            return
        print("文件大小: ", self.local_file_size)
        self.local_file_basename = os.path.basename(selected_file)
        self.local_file_ipt.setText(selected_file)

    def draw_progress_bar(self):
        self.progress_bar.setGeometry(10, 300, 480, 30)
        style = """
                QProgressBar {
                    border: 2px solid grey;
                    border-radius: 5px;
                    text-align: center;
                }

                QProgressBar::chunk {
                    background-color: #37DA7E;
                    width: 20px;
                }"""
        self.progress_bar.setStyleSheet(style)

    def print_progress(self, transferred, toBeTransferred):
        print("Transferred: {0}\tOut of: {1}".format(transferred, toBeTransferred))
        per = int(transferred / toBeTransferred * 100)
        self.timer_callback(per)

    def timer_callback(self, step):
        if self.step >= 100:
            self.timer.stop()
            return
        self.step = step
        print("step is {}".format(self.step))
        self.progress_bar.setValue(self.step)
        #refresh ui
        QApplication.processEvents()

    def draw_upload_button(self):
        self.btn = QPushButton('立即上传', self)
        self.btn.resize(self.btn.sizeHint())
        self.btn.move(50, 400)
        self.btn.clicked.connect(self.scp_upload)

    def init_ui(self):
        self.get_local_account_info()
        self.draw_ip_input()
        self.draw_port_input()
        self.draw_auth_type()
        self.draw_user_input()
        self.draw_pwd_input()
        self.draw_local_input()
        self.draw_remote_input()
        self.draw_upload_button()
        self.draw_progress_bar()
        self.setGeometry(300, 300, 500, 450)
        self.setWindowTitle(u'SCP上传文件')
        self.show()

    @staticmethod
    def right_ip(ip):
        p = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
        if p.match(ip):
            return True
        else:
            return False

    def scp_upload(self):
        ip = self.ip_input.text().strip()
        if ip == '':
            self.alert("请输入服务器ip")
            return False
        else:
            if not self.right_ip(ip):
                self.alert("请输入格式正确的服务器ip，如：255.255.255.0")
                return False

        port = self.port_input.text().strip()
        if port == '':
            self.alert("请输入端口")
            return False
        user = self.user_input.text().strip()
        if user == '':
            self.alert("请输入登录账号")
            return False
        pwd = self.pwd_input.text().strip()
        if pwd == '':
            self.alert("请输入登录密码")
            return False
        local_file = self.local_file_ipt.text().strip()
        if local_file == '':
            self.alert("请选择本地文件")
            return False
        elif os.path.isdir(local_file):
            self.alert("{} 不是有效的文件".format(local_file))
            return False
        remote_file = self.rem_file_input.text().strip()
        if remote_file == '':
            self.alert("请输入远程文件保存路径")
            return False
        else:
            end = remote_file.endswith("/")
            have_point = "." in remote_file
            if end or not have_point:
                self.alert("{} 不是有效的文件名".format(remote_file))
                return False

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port, user, pwd)
        a = ssh.exec_command('date')
        stdin, stdout, stderr = a
        print(stdout.read())
        paramiko.SFTPClient.from_transport(ssh.get_transport())
        sftp_open = ssh.open_sftp()
        sftp_open.put(local_file, remote_file, callback=self.print_progress)
        sftp_open.close()
        ssh.close()
        self.set_local_account_info()
        self.alert("文件" + local_file + "上传完成\n上传路径为：" + remote_file)

    def alert(self, msg):
        QMessageBox.information(self, "系统提示", msg, QMessageBox.Ok)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    scpUpload = ScpUpload()
    sys.exit(app.exec_())

