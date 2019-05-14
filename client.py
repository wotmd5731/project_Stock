
# -*- coding: utf-8 -*-

#!/usr/bin/env python3

#import socket
#
#HOST = '127.0.0.1'  # The server's hostname or IP address
#PORT = 65432        # The port used by the server
#
#
#from multiprocessing.managers import BaseManager
#class QueueManager(BaseManager): pass
#
#QueueManager.register('get_class')
#m = QueueManager(address=(HOST, PORT), authkey=b'abc')
#m.connect()
#fun = m.get_class()
#
#print(fun('comm_connect',0))


from multiprocessing.connection import Client
from array import array

address = ('localhost', 6000)
conn = Client(address, authkey=b'abc')

print (conn.recv())                 # => [2.25, None, 'junk', float])

print( conn.recv_bytes()    )        # => 'hello'

arr = array('i', [0, 0, 0, 0, 0])
#print (conn.recv_bytes_into(arr))     # => 8
print (arr     )                    # => array('i', [42, 1729, 0, 0, 0])

conn.close()


#queue.put('hello')
#print(kiwoom.aa())



#  Test Code
#kiwoom = Kiwoom()
#kiwoom.comm_connect()
#print(kiwoom.get_connect_state())
#print(kiwoom.aa())

#data = kiwoom.get_data_opt10086("035420", "20170101")
#print(len(data))