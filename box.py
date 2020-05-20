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
        self.init_ui()

    def draw_local_file_select(self):
        box = QHBoxLayout()
        box.addWidget(self.local_file_ipt)
        self.local_file_btn.setText("选择文件")
        box.addWidget(self.local_file_btn)
        return box

    def draw_form(self):
        self.form_layout.setAlignment(QtCore.Qt.AlignLeft)
        self.form_layout.setLabelAlignment(QtCore.Qt.AlignLeft)
        self.ip_input.setAlignment(QtCore.Qt.AlignLeft)
        self.form_layout.addRow("&请输入服务器ip:", self.ip_input)
        self.form_layout.addRow("&请输入端口:", self.port_input)
        self.form_layout.addRow("&请输入登录账号:", self.user_input)
        self.form_layout.addRow("&请输入登录密码:", self.pwd_input)
        self.form_layout.addRow("&请输入本地文件:", self.draw_local_file_select())

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

