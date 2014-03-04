#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: sammko
# @Date:   2014-02-26 18:21:59
# @Last Modified by:   sammko
# @Last Modified time: 2014-03-04 17:18:34
import socket, ast, pickle

PTYPE_LEN = 4
PLEN_LEN  = 8

TCP_IP = '127.0.0.1'
TCP_PORT = 28135
MESSAGE = "*XYR0000"

xy = [0, 2]

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

packet_data = s.recv(2048)
if packet_data.startswith(">AUTH"):
    s.send("asd11b83")
s.send(MESSAGE)

s.send(str(len(str(xy))).zfill(8))
s.send(str(xy))
s.recv(4)
l = int(s.recv(8))
packet_data = int(s.recv(l))

print str(l)+"\n"+str(packet_data)

s.close()