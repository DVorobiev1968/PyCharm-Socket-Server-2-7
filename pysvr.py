# -*- coding: utf-8 -*-

import sys, string, getopt, thread, socket
from MesPacked import MesPacked
from PLCGlobals import PLCGlobals
from Nodes import Nodes, Objs

def main():
    mesPacked = MesPacked()
    nodes = Nodes()
    objs = Objs()
    try:
        opts, args = getopt.getopt(sys.argv[1:], "")
        if len(args) > 1:
            raise getopt.error, "Too many arguments."
    except getopt.error, msg:
        usage(msg)
    for o, a in opts:
        pass
    if args:
        try:
            port = string.atoi(args[0])
        except ValueError, msg:
            usage(msg)
    else:
        if PLCGlobals.PORT < 1:
            port = mesPacked.port
        else:
            port = PLCGlobals.PORT
    main_thread(port)


def usage(msg=None):
    sys.stdout = sys.stderr
    if msg:
        print msg
    print "\n", __doc__,
    sys.exit(2)


def main_thread(port):
    global mesPacked

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if len(PLCGlobals.host) < 1:
        sock.bind(("localhost", port))
    else:
        sock.bind((PLCGlobals.host, port))
    sock.listen(5)
    mesPacked.print_message("Listening on port:{0:d}...".format(port), PLCGlobals.INFO)

    while 1:
        (conn, addr) = sock.accept()
        if addr[0] != conn.getsockname()[0]:
            conn.close()
            mesPacked.print_message("Refusing connection from non-local host:{0:s}...".format(addr[0]),
                                    PLCGlobals.ERROR)
            continue
        thread.start_new_thread(service_thread, (conn, addr))
        del conn, addr


def service_thread(conn, addr):
    global mesPacked
    (caddr, cport) = addr
    mesPacked.print_message("Thread {0:s} has connection from {1:s}.".format(str(thread.get_ident()), caddr),
                            PLCGlobals.INFO)
    stdin = conn.makefile("r")
    stdout = conn.makefile("w", 0)
    # run_interpreter(stdin, stdout)
    run_parser(stdin, stdout)
    mesPacked.print_message("Thread {0:s} is done.".format(str(thread.get_ident())), PLCGlobals.INFO)


def run_interpreter(stdin, stdout):
    global mesPacked
    data = stdin.readline()
    mesPacked.recvMessage(data)
    stdout.write(mesPacked.nodeStruct.o_obj.b_message)
    mesPacked.print_message("b_message:{0}".format(mesPacked.nodeStruct.o_obj.b_message), PLCGlobals.INFO)

def loadObjs(id_node,h_idObj,h_idSubObj,d_value):
    objs = Objs()
    objs.set_val(h_idObj,"h_idObj",h_idObj)
    objs.set_val(h_idObj,"h_idSubObj",h_idSubObj)
    objs.set_val(h_idObj,"i_typeData",objs.mesPacked.dict_typeData["Float"])
    objs.set_val(h_idObj,"d_value",d_value)
    objs.mesPacked.initNodeStruct(id_node,h_idObj,h_idSubObj,d_value)
    objs.set_val(h_idObj, "b_message")
    objs.set_val(h_idObj, "i_check")
    return objs

def set_nodes(id_node, h_idObj,h_idSubObj,d_value):
    global nodes
    nodes.set_val(id_node, "i_idNode", id_node)
    nodes.set_val(id_node, "i_code_answer", nodes.mesPacked.OK)
    nodes.set_val(id_node, "i_codeCommand", nodes.mesPacked.CODE_START)
    nodes.set_val(id_node, "s_command", nodes.mesPacked.dict_classif[nodes.mesPacked.CODE_START])
    nodes.set_val(id_node, "s_message", nodes.mesPacked.dict_classif[nodes.mesPacked.OK])
    nodes.set_val(id_node, "Objs", loadObjs(id_node,h_idObj,h_idSubObj,d_value))


def run_parser(stdin, stdout):
    """
    функция обрабатывает входное сообщение от клиента и готовит ответ, при этом проверяя контрольную сумму
    пока от клиента не придет i_codeCommand=CODE_STOP
    :param stdin:
    :param stdout:
    :return:
    """
    data = stdin.readline()
    nodeStruct=mesPacked.nodeStruct
    while nodeStruct.i_codeCommand!=mesPacked.CODE_EXIT:
        i_status, nodeStruct = mesPacked.recvMessageNode(data)
        if nodeStruct.i_codeCommand==mesPacked.CODE_START:
            if i_status==mesPacked.OK:
                stdout.write(nodeStruct.o_obj.b_message)
                mesPacked.print_message("b_message:{0}".format(nodeStruct.o_obj.b_message), PLCGlobals.BREAK_DEBUG)
                data = stdin.readline()
                i_status, nodeStruct=mesPacked.recvMessageNode(data)
            else:
                pass
        elif nodeStruct.i_codeCommand==mesPacked.CODE_LIST_NODES:
            mesPacked.print_message("Start listing nodes, recieve code:{0}...".format(nodeStruct.i_codeCommand), PLCGlobals.INFO)
            break
        else:
            pass

            # последнаая ответка после чего завершаем сеанс, закываем поток
            # stdout.write(nodeStruct.o_obj.b_message)
            # mesPacked.print_message("b_message:{0}".format(nodeStruct.o_obj.b_message), PLCGlobals.INFO)

main()
