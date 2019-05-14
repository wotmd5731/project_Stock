#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket
import json


HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 50007              # Arbitrary non-privileged port
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while True:
            print('a')
            data = conn.recv(2048)
            aa = json.loads(data)
            print(aa['a'])
            print(aa['b'])
            if not data: 
                print('brake')
                break
            conn.sendall(b'a')
                