# -*- coding: utf-8 -*-

import socket
import json

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


HOST = '127.0.0.1'    # The remote host
PORT = 50007              # The same port as used by the server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    ret = remote_inst(s,'fa',[1])
    print(ret)

