#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2020/5/20 4:44 PM
# @Author  : Aries (i@iw3c.com)
# @Site    : http://iw3c.com
# @File    : layout.py
# @Software: PyCharm

from PyQt5 import QtCore
from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QFileDialog,
                             QPushButton, QApplication, QMessageBox, QProgressBar, QVBoxLayout, QRadioButton, QHBoxLayout, QFormLayout)
import paramiko
import os
import sys
import re
import json


class IsScp(QWidget):
    def __init__(self):
        super().__init__()
        self.timer = QtCore.QBasicTimer()
        self.step = 0
        self.local_file_size = 0
        self.auth_key_file_size = 0
        self.local_file_basename = ""
        self.local_account_info_db = os.getcwd()+"/info.db"
        self.account_info = {
            "ip":"",
            "port":"",
            "user":"",
            "pwd":"",
            "remote_file":"",
        }
        self.form_layout = QFormLayout(self)
        self.ip_input = QLineEdit(self)
        self.port_input = QLineEdit(self)
        self.user_input = QLineEdit(self)
        self.pwd_input = QLineEdit(self)
        self.local_file_ipt = QLineEdit(self)
        self.local_file_btn = QPushButton(self)
        self.remote_file_ipt = QLineEdit(self)
        self.auth_type_pwd = QRadioButton(self)
        self.auth_type_key = QRadioButton(self)
        self.auth_key_ipt = QLineEdit(self)
        self.auth_key_btn = QPushButton(self)
        self.auth_key_widget = QWidget(self)
        self.init_ui()

    def draw_auth_key_file_select(self):
        box = QHBoxLayout()
        box.addWidget(self.auth_key_ipt)
        self.auth_key_btn.setText("...")
        box.addWidget(self.auth_key_btn)
        self.auth_key_btn.clicked.connect(self.select_auth_key_file)
        self.auth_key_widget.setLayout(box)
        return self.auth_key_widget

    def draw_local_file_select(self):
        box = QHBoxLayout()
        box.addWidget(self.local_file_ipt)
        self.local_file_btn.setText("...")
        box.addWidget(self.local_file_btn)
        self.local_file_btn.clicked.connect(self.select_file)
        return box

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

    def draw_auth_type(self):
        box = QHBoxLayout()
        self.auth_type_key.setText("密钥")
        self.auth_type_pwd.setText("账号/密码")
        self.auth_type_pwd.setChecked(True)
        box.addWidget(self.auth_type_pwd)
        box.addWidget(self.auth_type_key)
        self.auth_type_pwd.toggled.connect(self.on_radio_button_toggled)
        return box

    def on_radio_button_toggled(self):
        if self.auth_type_pwd.isChecked():
            self.auth_key_widget.hide()
        elif self.auth_type_key.isChecked():
            self.auth_key_widget.show()

    def draw_form(self):
        self.form_layout.setAlignment(QtCore.Qt.AlignLeft)
        self.form_layout.setLabelAlignment(QtCore.Qt.AlignLeft)
        self.form_layout.setVerticalSpacing(15)
        self.ip_input.setAlignment(QtCore.Qt.AlignLeft)
        self.pwd_input.setEchoMode(QLineEdit.Password)
        self.form_layout.addRow("请输入服务器ip:", self.ip_input)
        self.form_layout.addRow("请输入端口:", self.port_input)
        self.form_layout.addRow("请选择验证方式:", self.draw_auth_type())
        self.form_layout.addRow("请选择证书:", self.draw_auth_key_file_select())
        self.form_layout.addRow("请输入登录账号:", self.user_input)
        self.form_layout.addRow("请输入登录密码:", self.pwd_input)
        self.form_layout.addRow("请选择要上传的文件:", self.draw_local_file_select())
        self.form_layout.addRow("请输入远程文件保存路径:", self.remote_file_ipt)

    def init_ui(self):
        self.setWindowTitle("SCP 上传文件")
        self.draw_form()
        self.resize(400, 100)
        self.setLayout(self.form_layout)
        self.show()

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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    scpUpload = IsScp()
    sys.exit(app.exec_())

