#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket
import json


HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 50007              # Arbitrary non-privileged port

def fa(aa):
    print('fa:',aa)
    return 'fa:aa'

def fb(aa):
    print('fb:',aa)
    return 'fb:abba'

def remote_inst(s,fname,farg):
    data = json.dumps({'name':fname,'arg':farg})
    s.send(bytes(data,'utf-8'))
    data = s.recv(1024)
    recvdata = json.loads(data.decode('utf-8'))
    return recvdata

def remote_call(s):
    data = s.recv(1024)
    print(data)
    if not data:return -1
    recvdata = json.loads(data.decode('utf-8'))
    ret = eval(recvdata['name']+'('+str(recvdata['arg'])+')')
    data = json.dumps([ret])
    s.send(bytes(data,'utf-8'))



with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while True:
            print('a')
            ret = remote_call(conn)
            if ret == -1:
                break
