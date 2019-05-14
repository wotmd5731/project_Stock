# -*- coding: utf-8 -*-

import socket
import json


HOST = '127.0.0.1'    # The remote host
PORT = 50007              # The same port as used by the server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    dd = json.dumps({'a':[1,23,3,4,5],'b':"123213"})
    
    
    s.send(bytes(dd,"utf-8"))
    
    data = s.recv(1024)
print('Received', repr(data))