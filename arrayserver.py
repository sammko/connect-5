#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: sammko
# @Date:   2014-02-25 13:57:01
# @Last Modified by:   sammko
# @Last Modified time: 2014-03-04 16:47:42

from colorama import init, Fore
import socket, threading, re, time, ast

class SharedData():
	gamefield = [[00,01,02],
				 [10,11,12],
				 [20,21,22]]
	unames = []

class ClientThread(threading.Thread):
	def __init__(self, ip, port, socket, i, shared):
		threading.Thread.__init__(self)
		self.ip = ip
		self.port = port
		self.socket = socket
		self.i = i
		self.a = 1
		self.shared = shared
		shared.unames.append("player_"+str(i))
		print Fore.GREEN + "[+]" + Fore.RESET + " New thread ("+str(i)+") for "+ip+":"+str(port)

	def run(self):    
		self.socket.send(">AUTH"+str(self.i))
		if not self.socket.recv(8) == auth:
			self.a = 0
			print Fore.CYAN+"[!]"+Fore.RESET+" Client ("+str(self.i)+") not authorized! Killing!"
			self.socket.send(">NAUTH")
		if self.a:
			print Fore.CYAN+"[!]"+Fore.RESET+" Client ("+str(self.i)+") authorized successfully!"
		data = "."
		while True and self.a:
			data = self.socket.recv(8)
			if not len(data): break
			print Fore.YELLOW+"Client ("+str(self.i)+") sent: "+Fore.RESET+data
			if data == "-FAR0000":									#FULL ARRAY REQUEST (W/O DATA)
				dmp = str(self.shared.gamefield).replace(" ", "")	#ARRAY STRING
				l = str(len(dmp)).zfill(8)							#PACKET LENGHT (FIXED 8 DIG)
				self.socket.send(">FAR")							#SEND PACKET TYPE (FULL ARRAY REQUEST)
				self.socket.send(l)									#SEND PACKET LEN
				self.socket.send(dmp)								#SEND PACKET DATA
				print Fore.CYAN+"Client ("+str(self.i)+") FULL ARRAY REQ -> l: "+l+Fore.RESET

			if data == "+SFA0000":									#SET FULL ARRAY (W/ DATA)
				l = int(self.socket.recv(8))						#RECV DATA LEN
				dmp = self.socket.recv(l)							#RECV DATA
				self.shared.gamefield = ast.literal_eval(dmp)		#WRITE ARRAY
				self.socket.send(">SFA")							#SEND ACK
				print Fore.CYAN+"Client ("+str(self.i)+") SET FULL ARRAY <- l: "+str(l)

			if data == "*XYR0000":									#XY REQUEST (W/ DATA DUPLEX)
				l = int(self.socket.recv(8))						#RECV DATA LEN
				dmp = self.socket.recv(l)							#RECV DATA
				xy = ast.literal_eval(dmp)							#WRITE ARRAY (needs safe-checking)
				self.socket.send(">XYR")							#SEND ACK
				dmp = str(self.shared.gamefield[xy[0]][xy[1]]).replace(" ", "")#CREATE DATA DUMP
				l = str(len(dmp)).zfill(8)							#PACKET LENGHT (FIXED 8 DIG)
				self.socket.send(l)									#SEND PACKET LEN
				self.socket.send(dmp)								#SEND PACKET DATA
				print Fore.CYAN+"Client ("+str(self.i)+") GET XY <> l: "+l

			if data == "+XYS0000":									#XY SET (W/ DATA)
				l = int(self.socket.recv(8))						#RECV DATA LEN
				dmp = self.socket.recv(l)							#RECV DATA
				xyd = ast.literal_eval(dmp)							#WRITE ARRAY (needs safe-checking)
				self.shared.gamefield[xyd[0]][xyd[1]] = int(xyd[2])	#WRITE DATA TO GFIELD
				self.socket.send(">XYS")							#SEND ACK
				print Fore.CYAN+"Client ("+str(self.i)+") SET XY <- l: "+str(l)

			if data == "+SUN0000":									#SET USERNAME (W/ DATA)
				l = int(self.socket.recv(8))						#RECV DATA LEN
				dmp = self.socket.recv(l)							#RECV DATA
				self.shared.unames[self.i] = dmp					#WRITE TO SHARED
				self.socket.send(">SUN")							#SEND ACK
				print Fore.CYAN+"Client ("+str(self.i)+") SET UN <- l: "+str(l)

			if data == "-GUN0000":									#GET USERNAME (W/O DATA)
				self.socket.send(">GUN")							#SEND ACK
				dmp = self.shared.unames[self.i]					#DUMP DATA
				l = str(len(dmp)).zfill(8)							#DUMP LEN
				self.socket.send(l)									#SEND LEN
				self.socket.send(dmp)								#SEND DATA
				print Fore.CYAN+"Client ("+str(self.i)+") GET UN <- l: "+l

			if data == "-LAP0000":									#LIST ALL PLAYERS (W/O DATA)
				self.socket.send(">LAP")							#SEND ACK
				dmp = str(self.shared.unames)						#DUMP DATA
				l = str(len(dmp)).zfill(8)							#DUMP LEN
				self.socket.send(l)									#SEND LEN
				self.socket.send(dmp)								#SEND DATA
				print Fore.CYAN+"Client ("+str(self.i)+") GET PL <- l: "+l

		self.shared.unames[self.i] = ''
		print Fore.RED + "[-]" + Fore.RESET + " Client ("+str(self.i)+") disconnected...\n"

DEBUG = 1

host = "0.0.0.0"
port = 28135

auth = "asd11b83"

tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

tcpsock.bind((host,port))
threads = []
i = 0

print Fore.BLUE + "Listening on "+host+":"+str(port)+Fore.RESET+"\n\n"

s = SharedData()

while True:
	tcpsock.listen(4)
	(clientsock, (ip, port)) = tcpsock.accept()
	newthread = ClientThread(ip, port, clientsock, i, s)
	i = i + 1
	newthread.start()
	threads.append(newthread)

for t in threads:
	t.join()