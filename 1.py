#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2020/5/21 1:40 下午
# @Author  : Aries (i@iw3c.com)
# @Site    : http://iw3c.com
# @File    : 1.py
# @Software: PyCharm


def test_func():
    with open("test.log", "a+") as f:
        for i in range(10):
            f.write("This is line %d\r\n" % (i + 1))


if __name__ == '__main__':
    test_func()
