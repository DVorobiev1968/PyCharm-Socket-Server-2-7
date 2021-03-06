# -*- coding: utf-8 -*-

import getopt, sys
from time import sleep

from Client.SocketClient import SocketClient
from Server.PLCGlobals import PLCGlobals

global socketClient

def usage(msg=None):
    sys.stdout = sys.stderr
    if msg:
        print(msg)
    print("\n", __doc__)
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
        except IndexError:
            socketClient = SocketClient('localhost', 8889)
    else:
        socketClient = SocketClient()

def test_node():
    module=sys.argv[0].split('/')[-1].split('.')[0]
    sys_info="Starting {0} from Python:{1}.{2}\n".format(module,sys.version_info.major, sys.version_info.minor)
    print (sys_info)
    PLCGlobals.debug = PLCGlobals.BREAK_DEBUG
    # PLCGlobals.debug = PLCGlobals.ERROR
    socketClient = SocketClient('localhost', 8889)
    d_value=socketClient.set_socket_node(1,0x1000,socketClient.mesPacked.CODE_SINGLE_START,10.01)
    socketClient.mesPacked.print_message("d_value:{0:4.10f}".format(d_value), PLCGlobals.INFO)
    d_value_out=socketClient.set_socket_node(1+1,0x1000,socketClient.mesPacked.CODE_SINGLE_START,20.01)
    socketClient.mesPacked.print_message("d_value_out:{0:4.10f}".format(d_value_out), PLCGlobals.INFO)
    d_value_src = socketClient.load_for_algoritm(1, 0x1000)
    d_value_out = socketClient.load_for_algoritm(1 + 1, 0x1000)
    d_value_out = 0 - d_value_src
    sleep(0.02)
    d_value_src = socketClient.save_for_algoritm(1, 0x1000, d_value_src)
    d_value_out = socketClient.save_for_algoritm(2, 0x1000, d_value_out)
    socketClient.mesPacked.print_message("d_value_src:{0:4.10f}".format(d_value_src), PLCGlobals.INFO)
    socketClient.mesPacked.print_message("d_value_out:{0:4.10f}".format(d_value_out), PLCGlobals.INFO)


def beremiz_simulation():
    module=sys.argv[0].split('/')[-1].split('.')[0]
    sys_info="Starting {0} from Python:{1}.{2}\n".format(module,sys.version_info.major, sys.version_info.minor)
    print (sys_info)
    # PLCGlobals.debug = PLCGlobals.BREAK_DEBUG
    PLCGlobals.debug = PLCGlobals.ERROR
    loadParameters()
    d_value=socketClient.set_socket_node(1,0x1000,socketClient.mesPacked.CODE_SINGLE_START,10.01)
    # d_value=socketClient.set_socket_node(2,0x1000,socketClient.mesPacked.CODE_SINGLE_START,0.01)
    # socketClient.mesPacked.print_message("socketClient.set_socket_node:{0:4.10f}".format(d_value), PLCGlobals.INFO)
    # d_value_3=socketClient.load_socket_node(1, 0x1000)
    # d_value=socketClient.load_socket_node(1, 0x1000)
    while True:
        # d_value_src=socketClient.load_socket_node(1, 0x1000)
        d_value_src=socketClient.load_for_algoritm(1, 0x1000)
        d_value=socketClient.load_for_algoritm(1+1, 0x1000)
        # d_value_1=pow(d_value_src,2)
        d_value_1=0-d_value_src
        sleep(0.020)
        d_value_src=socketClient.save_for_algoritm(1,0x1000,d_value_src)
        d_value_2=socketClient.save_for_algoritm(1+1,0x1000,d_value_1)
        sleep(0.020)
        # d_value_3=socketClient.load_socket_node(1, 0x1000)
        if d_value_src!=0:
            socketClient.mesPacked.print_message("d_value:{0:4.10f}".format(d_value), PLCGlobals.INFO)
            socketClient.mesPacked.print_message("d_value_1:{0:4.10f}".format(d_value_1), PLCGlobals.INFO)
            socketClient.mesPacked.print_message("d_value_2:{0:4.10f}".format(d_value_2), PLCGlobals.INFO)
            socketClient.mesPacked.print_message("d_value_src:{0:4.10f}".format(d_value_src), PLCGlobals.INFO)
        # break

if __name__ == '__main__':
    beremiz_simulation()
