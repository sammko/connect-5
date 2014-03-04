#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: sammko
# @Date:   2014-02-25 14:15:23
# @Last Modified by:   sammko
# @Last Modified time: 2014-02-26 18:07:18
import socket, ast, pickle

PTYPE_LEN = 4
PLEN_LEN  = 8

TCP_IP = '127.0.0.1'
TCP_PORT = 28135
MESSAGE = "-FAR0000"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

packet_data = s.recv(2048)
if packet_data.startswith(">AUTH"):
	s.send("asd11b83")
s.send(MESSAGE)

packet_type = s.recv(PTYPE_LEN)
packet_len  = int(s.recv(PLEN_LEN))
packet_data = s.recv(packet_len)
packet_array=ast.literal_eval(packet_data)
print packet_type+"\n"+str(packet_len)+"\n"+str(packet_array)

s.close()