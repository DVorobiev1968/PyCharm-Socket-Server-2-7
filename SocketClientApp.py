# -*- coding: utf-8 -*-
import getopt
import sys

from SocketClient import SocketClient
from PLCGlobals import PLCGlobals

global socketClient

def usage(msg=None):
    sys.stdout = sys.stderr
    if msg:
        print(msg)
    print("\n", __doc__, end=' ')
    sys.exit(2)

def loadParameters():
    global socketClient
    try:
        opts, args = getopt.getopt(sys.argv[1:], "")
        if len(args) > 2:
            raise getopt.error("Too many arguments.")
    except getopt.error as msg:
        usage(msg)
    for o, a in opts:
        pass
    if args:
        try:
            host = args[0]
            port = int(args[1])
            socketClient = SocketClient(host, port)
            return 0
        except ValueError as msg:
            usage(msg)
            return -1
    else:
        socketClient = SocketClient()

loadParameters()
d_value_1=0
# d_value_1=socketClient.load_for_algoritm(1, 0x1000+7)
socketClient.set_socket_node(2,0x1000+7,socketClient.mesPacked.CODE_SINGLE_START,1968)
d_value=socketClient.load_socket_node(2, 0x1000+7)
socketClient.mesPacked.print_message("d_value:{0:4.10f}".format(d_value), PLCGlobals.INFO)
socketClient.mesPacked.print_message("d_value_1:{0:4.10f}".format(d_value_1), PLCGlobals.INFO)
socketClient.set_socket_node(3,0x1000+7,socketClient.mesPacked.CODE_SINGLE_START,1968)