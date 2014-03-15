#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: sammko
# @Date:   2014-02-25 13:57:01
# @Last Modified by:   sammko
# @Last Modified time: 2014-03-15 22:01:38

from colorama import init, Fore
import socket, threading, re, time, ast

class SharedData():
    gamefield = [[00,01,02],
                 [10,11,12],
                 [20,21,22]]
    unames = []

class Packet():
    def __init__(self, payload):
        self.payload = payload

    def get_len_int(self):
        return len(self.payload)

    def get_len(self):
        return str(len(self.payload)).zfill(8) 

    def get_payload(self):
        return self.payload

class PacketDispatcher():
    def __init__(self, socket):
        self.socket = socket

    def dispatch(self, packet):
        self.socket.send(packet.get_len())
        ack = self.socket.recv(4)
        if (ack == "_ACK"):
            self.socket.send(packet.get_payload())
        return ack

class PacketReceiver():
    def __init__(self, socket):
        self.socket = socket

    def receive(self):
        l = int(self.socket.recv(8))
        self.socket.send("_ACK")
        return Packet(self.socket.recv(l))

class ClientThread(threading.Thread):
    def __init__(self, ip, port, socket, i, shared):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.socket = socket
        self.i = i
        self.a = 1
        self.disp = PacketDispatcher(socket)
        self.recv = PacketReceiver(socket)
        self.shared = shared
        shared.unames.append("player_"+str(i))
        print(Fore.GREEN + "[+]" + Fore.RESET + " New thread ("+str(i)+") for "+ip+":"+str(port))

    def run(self):   
        self.authenticate() 
        data = "."
        while True and self.a:
            data = self.recv.receive().get_payload()
            if not len(data): break
            print(Fore.YELLOW+"Client ("+str(self.i)+") sent: "+Fore.RESET+data)
            self.parse_cmd(data)
            
        self.shared.unames[self.i] = ''
        self.socket.close()
        print(Fore.RED + "[-]" + Fore.RESET + " Client ("+str(self.i)+") disconnected...\n")

    def authenticate(self):
        self.disp.dispatch(Packet(">AUTH"+str(self.i)))
        code = self.recv.receive().get_payload()
        if not code == auth:
            self.a = 0
            print(Fore.CYAN+"[!]"+Fore.RESET+" Client ("+str(self.i)+") not authorized! Killing!")
            self.disp.dispatch(Packet(">NAUT"+str(self.i)))
        if self.a:
            print(Fore.CYAN+"[!]"+Fore.RESET+" Client ("+str(self.i)+") authorized successfully!")
            self.disp.dispatch(Packet(">SAUT"+str(self.i)))

    def parse_cmd(self, data):
        if data == "-GFA0000":                                  #FULL ARRAY REQUEST (W/O DATA)
            dmp = str(self.shared.gamefield).replace(" ", "")   #ARRAY STRING
            self.disp.dispatch(Packet(dmp))                     #SEND DATA DUMP
            print(Fore.CYAN+"Client ("+str(self.i)+") GET FA"+Fore.RESET)

        if data == "+SFA0000":                                  #SET FULL ARRAY (W/ DATA)
            dmp = self.recv.receive().get_payload()             #RECEIVE PACKET
            self.shared.gamefield = ast.literal_eval(dmp)       #WRITE ARRAY
            self.disp.dispatch(Packet(">SFA"))                  #SEND ACK
            print(Fore.CYAN+"Client ("+str(self.i)+") SET FA")

        if data == "*XYR0000":                                  #XY REQUEST (W/ DATA TWOWAY)
            dmp = self.recv.receive().get_payload()             #RECEIVE XYLOC
            xy = ast.literal_eval(dmp)                          #WRITE ARRAY (needs safe-checking)
            dmp = str(self.shared.gamefield[xy[0]][xy[1]]).replace(" ", "")#CREATE DATA DUMP
            self.disp.dispatch(Packet(dmp))                     #SEND DATA
            print(Fore.CYAN+"Client ("+str(self.i)+") GET XY")

        if data == "+XYS0000":                                  #XY SET (W/ DATA)
            dmp = self.recv.receive().get_payload()             #RECEIVE DATA
            xyd = ast.literal_eval(dmp)                         #WRITE ARRAY (needs safe-checking)
            self.shared.gamefield[xyd[0]][xyd[1]] = int(xyd[2]) #WRITE DATA TO GFIELD
            self.disp.dispatch(Packet(">XYS"))
            print(Fore.CYAN+"Client ("+str(self.i)+") SET XY")

        if data == "+SUN0000":                                  #SET USERNAME (W/ DATA)
            dmp = self.recv.receive().get_payload()             #RECEIVE DATA
            self.shared.unames[self.i] = dmp                    #WRITE TO SHARED
            self.disp.dispatch(Packet(">SUN"))                  #SEND ACK
            print(Fore.CYAN+"Client ("+str(self.i)+") SET UN")

        if data == "-GUN0000":                                  #GET USERNAME (W/O DATA)
            dmp = self.shared.unames[self.i]                    #DUMP DATA
            self.disp.dispatch(Packet(dmp))                     #SEND DATA
            print(Fore.CYAN+"Client ("+str(self.i)+") GET UN")

        if data == "-LAP0000":                                  #LIST ALL PLAYERS (W/O DATA)
            dmp = str(self.shared.unames)                       #DUMP DATA
            self.disp.dispatch(Packet(dmp))                     #SEND DATA
            print(Fore.CYAN+"Client ("+str(self.i)+") GET PL")

        if data == "/DSC0000":                                  #DISCONNECT (0DATA)
            self.disp.dispatch(Packet(">DSC"))                  #SEND ACK
            self.a = 0                                          #USE DEAUTH TO KILL THREAD
            print(Fore.CYAN+"Client ("+str(self.i)+") FDSC")

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