# -*- coding: utf-8 -*-
import getopt, sys
from SocketClient import SocketClient
from PLCGlobals import PLCGlobals

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
    else:
        socketClient = SocketClient()

module=sys.argv[0].split('/')[-1].split('.')[0]
sys_info="Starting {0} from Python:{1}.{2}\n".format(module,sys.version_info.major, sys.version_info.minor)
print (sys_info)
loadParameters()
d_value_1=0
# d_value_1=socketClient.load_for_algoritm(1, 0x1000+7)
d_value=socketClient.set_socket_node(11,0x1000,socketClient.mesPacked.CODE_SINGLE_START,100.00000001)
socketClient.mesPacked.print_message("socketClient.set_socket_node:{0:4.10f}".format(d_value), PLCGlobals.INFO)
d_value=socketClient.load_socket_node(11, 0x1000)
socketClient.mesPacked.print_message("socketClient.load_socket_node:{0:4.10f}".format(d_value), PLCGlobals.INFO)
# # socketClient.mesPacked.print_message("d_value_1:{0:4.10f}".format(d_value_1), PLCGlobals.INFO)
# socketClient.set_socket_node(3,0x1000+7,socketClient.mesPacked.CODE_SINGLE_START,1968)