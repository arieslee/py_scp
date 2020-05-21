#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2020/5/20 4:44 PM
# @Author  : Aries (i@iw3c.com)
# @Site    : http://iw3c.com
# @File    : layout.py
# @Software: PyCharm

from PyQt5 import QtCore
from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QFileDialog,
                             QPushButton, QApplication, QMessageBox, QProgressBar, QRadioButton, QHBoxLayout, QFormLayout)
from PyQt5.QtGui import QIcon
import paramiko
import os
import sys
import re
import json
import time


class IsScp(QWidget):
    def __init__(self):
        super().__init__()
        self.timer = QtCore.QBasicTimer()
        self.step = 0
        self.local_file_size = 0
        self.auth_key_file_size = 0
        self.local_file_basename = ""
        self.is_upload = False
        self.auth_type = "pwd"
        is_script = False
        # 获取当前用䚮的根路径
        # print(os.path.expandvars('$HOME'))
        # print(os.environ['HOME'])
        if is_script:
            self.local_account_info_db = "./info.db"
            self.upload_log = "./upload.log"
            self.log_file = "./error.log"
        else:
            # 获取当前用䚮的根路径
            os_user_path = os.path.expanduser('~')
            self.local_account_info_db = os_user_path+"/scp_upload_info.db"
            self.upload_log = os_user_path+"/scp_upload_upload.log"
            self.log_file = os_user_path+"/scp_upload_error.log"

        self.account_info = {
            "ip": "",
            "port": "",
            "user": "",
            "pwd": "",
            "remote_file": "",
            "auth_type": self.auth_type,
            "auth_key_file": "",
        }
        self.form_layout = QFormLayout(self)
        self.ip_input = QLineEdit(self)
        self.port_input = QLineEdit(self)
        self.user_input = QLineEdit(self)
        self.local_file_ipt = QLineEdit(self)
        self.local_file_btn = QPushButton(self)
        self.remote_file_ipt = QLineEdit(self)
        self.auth_type_pwd = QRadioButton(self)
        self.auth_type_key = QRadioButton(self)
        self.pwd_input = None
        self.auth_key_ipt = None
        self.progress_bar = None
        self.submit_btn = None
        self.init_ui()

    def draw_auth_key_file_select(self):
        box = QHBoxLayout()
        self.auth_key_ipt = QLineEdit(self)
        box.addWidget(self.auth_key_ipt)
        btn = QPushButton(self)
        btn.setText("...")
        box.addWidget(btn)
        btn.clicked.connect(self.select_auth_key_file)
        return box

    def draw_local_file_select(self):
        box = QHBoxLayout()
        box.addWidget(self.local_file_ipt)
        self.local_file_btn.setText("...")
        box.addWidget(self.local_file_btn)
        self.local_file_btn.clicked.connect(self.select_file)
        return box

    def draw_auth_type(self):
        box = QHBoxLayout()
        self.auth_type_key.setText("密钥")
        self.auth_type_pwd.setText("账号/密码")
        self.auth_type_pwd.setChecked(True)
        box.addWidget(self.auth_type_pwd)
        box.addWidget(self.auth_type_key)
        self.auth_type_pwd.toggled.connect(self.on_radio_button_toggled)
        return box

    def make_pwd_input(self):
        self.pwd_input = QLineEdit(self)
        self.pwd_input.setEchoMode(QLineEdit.Password)

    def draw_pwd_input(self, row_num=4):
        self.make_pwd_input()
        self.form_layout.insertRow(row_num, "请输入登录密码:", self.pwd_input)
        self.pwd_input.setText(self.account_info["pwd"])

    def draw_auth_key_input(self, row_num=4):
        self.form_layout.insertRow(row_num, "请选择证书", self.draw_auth_key_file_select())
        self.auth_key_ipt.setText(self.account_info["auth_key_file"])

    def on_radio_button_toggled(self):
        if self.auth_type_pwd.isChecked():
            self.form_layout.removeRow(4)
            self.draw_pwd_input(4)
            self.auth_type = "pwd"
        elif self.auth_type_key.isChecked():
            self.form_layout.removeRow(4)
            self.draw_auth_key_input(4)
            self.auth_type = "key"

    def draw_progress_bar(self):
        self.progress_bar = QProgressBar(self)
        style = """
                QProgressBar {
                    border: 1px solid grey;
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
        # refresh ui
        QApplication.processEvents()

    def draw_submit_button(self):
        self.submit_btn = QPushButton(self)
        style = """
                        QPushButton {
                            background-color:#37DA7E;
                            border:0;
                            border-radius: 5px;
                            text-align: center;
                            color:#666666;
                            padding:10px;
                        }"""
        self.submit_btn.setStyleSheet(style)
        self.submit_btn.setText("立即上传")
        self.submit_btn.clicked.connect(self.on_submit)

    @staticmethod
    def right_ip(ip):
        p = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
        if p.match(ip):
            return True
        else:
            return False

    def alert(self, msg):
        QMessageBox.information(self, "系统提示", msg, QMessageBox.Ok)

    def on_submit(self):
        if self.is_upload:
            return False
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

        pwd = ''
        auth_key_file = ''

        if self.auth_type_pwd.isChecked():
            pwd = self.pwd_input.text().strip()
            if pwd == '':
                self.alert("请输入登录密码")
                return False
        else:
            auth_key_file = self.auth_key_ipt.text().strip()
            if auth_key_file == '':
                self.alert("请选择密钥")
                return False

        local_file = self.local_file_ipt.text().strip()
        if local_file == '':
            self.alert("请选择本地文件")
            return False
        elif os.path.isdir(local_file):
            self.alert("{} 不是有效的文件".format(local_file))
            return False
        remote_file = self.remote_file_ipt.text().strip()
        if remote_file == '':
            self.alert("请输入远程文件保存路径")
            return False
        else:
            end = remote_file.endswith("/")
            have_point = "." in remote_file
            if end or not have_point:
                self.alert("{} 不是有效的文件名".format(remote_file))
                return False
        self.is_upload = True
        self.run_ssh_upload(ip, port, user, pwd, auth_key_file, local_file, remote_file)

    def run_ssh_upload(self, ip, port, user, pwd, auth_key_file, local_file, remote_file):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if self.auth_type_pwd.isChecked():
                ssh.connect(ip, port, user, pwd)
            else:
                key = paramiko.RSAKey.from_private_key_file(auth_key_file)  # 有解密密码时,
                ssh.connect(ip, port, user, pkey=key)
            # private = paramiko.RSAKey.from_private_key_file(auth_key_file)
            # ssh.connect(ip, port, user, pwd)
            exec_cmd = ssh.exec_command('date')
            stdin, stdout, stderr = exec_cmd
            print(stdout.read())
            paramiko.SFTPClient.from_transport(ssh.get_transport())
            sftp_open = ssh.open_sftp()
            sftp_open.put(local_file, remote_file, callback=self.print_progress)
            sftp_open.close()
            ssh.close()
            self.set_local_account_info()
            self.alert("文件" + local_file + "上传完成\n上传路径为：" + remote_file)
            # 上传记录
            upload_log = self.merge_dict(self.account_info, {
                "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            })
            self.set_upload_log(upload_log)
            self.is_upload = False
        except Exception as e:
            print(e)
            self.set_local_account_info()
            self.alert("上传时发生错误")
            self.set_log(str(e))

    @staticmethod
    def merge_dict(a, b):
        res = {**a, **b}
        return res

    def set_upload_log(self, data):
        try:
            with open(self.upload_log, "a+", encoding='utf-8') as f:
                f.write(json.dumps(data) + "\n")
        except Exception as e:
            self.alert(str(e))

    def set_log(self, log_msg):
        try:
            with open(self.log_file, "a+", encoding='utf-8') as f:
                f.write(log_msg + "\n")
        except Exception as e:
            self.alert(str(e))


    def draw_form(self):
        self.form_layout.setAlignment(QtCore.Qt.AlignLeft)
        self.form_layout.setLabelAlignment(QtCore.Qt.AlignLeft)
        self.form_layout.setVerticalSpacing(15)
        self.ip_input.setAlignment(QtCore.Qt.AlignLeft)
        self.form_layout.addRow("请输入服务器ip:", self.ip_input)
        self.form_layout.addRow("请输入端口:", self.port_input)
        self.form_layout.addRow("请选择验证方式:", self.draw_auth_type())
        self.form_layout.addRow("请输入账号:", self.user_input)
        self.form_layout.addRow("请选输入本地文件文件:", self.draw_local_file_select())
        self.form_layout.addRow("请输入远程文件路径:", self.remote_file_ipt)
        self.draw_progress_bar()
        self.form_layout.addRow("上传进度:", self.progress_bar)
        self.draw_submit_button()
        self.form_layout.addRow("", self.submit_btn)
        # 密码输入框
        self.draw_pwd_input(4)
        # 载入上次保留的本地登录信息
        self.load_local_account_info()

    def init_ui(self):
        self.setWindowTitle("SCP 上传文件")
        self.setWindowIcon(QIcon("./assets/icon.png"))
        self.draw_form()
        self.resize(400, 100)
        self.setLayout(self.form_layout)
        self.show()

    def open_db_file(self):
        if os.path.isfile(self.local_account_info_db):
            file_handle = open(self.local_account_info_db, 'r', encoding='utf-8')
            return file_handle
        return False

    def load_local_account_info(self):
        file_handle = self.open_db_file()
        if not file_handle:
            return False

        data = file_handle.read()
        if data == "":
            return False

        file_handle.close()
        self.account_info = json.loads(data)
        self.ip_input.setText(self.account_info["ip"])
        self.port_input.setText(self.account_info["port"])
        self.user_input.setText(self.account_info["user"])
        self.remote_file_ipt.setText(self.account_info["remote_file"])
        if self.account_info["auth_type"] == "pwd":
            self.auth_type_pwd.setChecked(True)
            self.pwd_input.setText(self.account_info["pwd"])
        else:
            self.auth_type_key.setChecked(True)
            self.auth_key_ipt.setText(self.account_info["auth_key_file"])

    def set_local_account_info(self):
        try:
            auth_key_file = pwd_text = ""
            if self.auth_type_pwd.isChecked():
                pwd_text = self.pwd_input.text().strip()
            else:
                auth_key_file = self.auth_key_ipt.text().strip()

            with open(self.local_account_info_db, 'w+', encoding='utf-8') as f:
                data = {
                    "ip": self.ip_input.text().strip(),
                    "port": self.port_input.text().strip(),
                    "user": self.user_input.text().strip(),
                    "pwd": pwd_text,
                    "remote_file": self.remote_file_ipt.text().strip(),
                    "auth_type": self.auth_type,
                    "auth_key_file": auth_key_file,
                }
                json_str = json.dumps(data)
                f.write(json_str)
        except Exception as e:
            self.alert(str(e))

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
        # 获取文件大小
        self.local_file_size = os.path.getsize(selected_file)
        if self.local_file_size <= 0 :
            self.alert("选择的文件太小啦")
            return
        print("文件大小: ", self.local_file_size)
        self.local_file_ipt.setText(selected_file)

    def select_auth_key_file(self):
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
        # 获取文件大小
        self.auth_key_file_size = os.path.getsize(selected_file)
        if self.auth_key_file_size <= 0:
            self.alert("选择的文件太小啦")
            return
        print("文件大小: ", self.auth_key_file_size)
        self.auth_key_ipt.setText(selected_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    scpUpload = IsScp()
    sys.exit(app.exec_())

