# -*- coding: utf-8 -*-

import sys, string, getopt, socket

from MesPacked import MesPacked, NodeInfo
from Nodes import Nodes
from PLCGlobals import PLCGlobals

def loadSettings(key, mesPacked):
    if key==1:
        if len(PLCGlobals.host) < 1:
            return "localhost"
        else:
            return PLCGlobals.host
    elif key==2:
        if PLCGlobals.PORT < 1:
            return mesPacked.port
        else:
            return PLCGlobals.PORT
    else:
        pass

def usage(msg=None):
    sys.stdout = sys.stderr
    if msg:
        print msg
    print "\n", __doc__,
    sys.exit(2)

def load_socket_node(host, port, id_Node, id_Obj, idSubObj=0):
    global mesPacked
    # Create a socket (SOCK_STREAM means a TCP socket)
    sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    nodeStruct = NodeInfo()
    i_code_answer=0
    nodeStruct.i_idNode=id_Node
    nodeStruct.i_code_answer=i_code_answer
    nodeStruct.i_codeCommand=mesPacked.CODE_FIND_NODES
    nodeStruct.s_command=mesPacked.dict_classif[mesPacked.CODE_FIND_NODES]
    nodeStruct.s_message=mesPacked.dict_classif[i_code_answer]
    nodeStruct.o_obj.h_idObj=0x0+id_Obj
    nodeStruct.o_obj.h_idSubObj=0x0+idSubObj
    mesPacked.setB_message(0,nodeStruct)
    # Connect to server and send data
    sock.connect((host, port))
    sock.sendall(bytes(nodeStruct.o_obj.b_message))
    mesPacked.print_message("sendall: b_message:{0}".
                            format(nodeStruct.o_obj.b_message),
                            PLCGlobals.INFO)

    # Receive data from the server and shut down
    s_received = str(sock.recv(1024))
    i_status, nodeStruct = mesPacked.recvMessageNode(s_received)
    if (i_status!=mesPacked.SEARCH_FAIL):
        mesPacked.print_message("recvMessageNodes: b_message:{0}".
                            format(nodeStruct.o_obj.b_message),
                            PLCGlobals.INFO)
    else:
        mesPacked.print_message("recvMessageNodes: b_message:empty",
                            PLCGlobals.INFO)
    sock.close()

##############################################################
def main():
    global mesPacked, nodes, conn
    mesPacked = MesPacked()
    nodes=Nodes()
    conn=None

    try:
        opts, args = getopt.getopt(sys.argv[1:], "")
        if len(args) > 2:
            raise getopt.error, "Too many arguments."
    except getopt.error, msg:
        usage(msg)
    for o, a in opts:
        pass
    if args:
        try:
            host = args[0]
            port = string.atoi(args[1])
        except ValueError, msg:
            usage(msg)
    else:
        host = loadSettings(1, mesPacked)
        port = loadSettings(2, mesPacked)

    load_socket_node(host, port, 5, 0x1000+7)

main()