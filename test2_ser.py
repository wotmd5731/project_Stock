# -*- coding: utf-8 -*-
"""
Created on Tue May 14 22:42:00 2019

@author: JAE
"""

from multiprocessing.managers import BaseManager
import logging.config
from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtCore import QEventLoop
from PyQt5.QtWidgets import QApplication
import sys

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

class clss():
    def __init__(self):
        super().__init__()
        print('init')
        
    def aa(self,*args):
        print('aasdfasdfa')
        for arg in args:
            print(arg)
        return 'aaaa'


kk = clss()
class fclass():
    def func(name,*arg):
        global kk
        ret = getattr(kk,name)(*arg)
        print(ret)
        return ret
#    return kk.aa(*arg)

class QueueManager(BaseManager): 
    pass



QueueManager.register('func', callable=fclass)

m = QueueManager(address=(HOST, PORT), authkey=b'abc')
s = m.get_server()
s.serve_forever()

