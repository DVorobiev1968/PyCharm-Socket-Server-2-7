# -*- coding: utf-8 -*-

import sys, string, getopt, thread, socket
from MesPacked import MesPacked, NodeInfo
from PLCGlobals import PLCGlobals
from Nodes import Nodes

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

# global mesPacked, nodes
def main():
    global mesPacked, nodes, i_commandCode
    mesPacked = MesPacked()
    nodes = Nodes()
    i_commandCode=1

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

    main_thread(host, port)


def usage(msg=None):
    sys.stdout = sys.stderr
    if msg:
        print msg
    print "\n", __doc__,
    sys.exit(2)

def main_thread(host, port):
    global mesPacked, i_commandCode
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.bind((host, port))
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

        mesPacked.print_message("Close thread, recieve code:{0}...".
                                format(i_commandCode),
                                PLCGlobals.INFO)

        if i_commandCode==mesPacked.CODE_EXIT_SERVER:
            del conn, addr
            break
        del conn, addr


def service_thread(conn, addr):
    # global mesPacked
    global i_commandCode

    (caddr, cport) = addr
    mesPacked.print_message("Thread {0:s} has connection from {1:s}.".format(str(thread.get_ident()), caddr),
                            PLCGlobals.INFO)
    stdin = conn.makefile("r")
    stdout = conn.makefile("w", 0)
    # run_interpreter(stdin, stdout)
    run_parser(stdin, stdout)
    mesPacked.print_message("Thread {0:s} is done. i_codeCommand {1}.".
                            format(str(thread.get_ident()),i_commandCode), PLCGlobals.INFO)
    if i_commandCode == mesPacked.CODE_EXIT_SERVER:
        del conn, addr
        mesPacked.print_message("sys.exit(0)", PLCGlobals.INFO)
        exit(0)


def run_interpreter(stdin, stdout):
    # global mesPacked
    data = stdin.readline()
    mesPacked.recvMessage(data)
    stdout.write(mesPacked.nodeStruct.o_obj.b_message)
    mesPacked.print_message("b_message:{0}".format(mesPacked.nodeStruct.o_obj.b_message), PLCGlobals.INFO)


def loadObjs(nodeStruct):
    """
    Функция сохранения объекта в узле в краткосрочном хранилище
    :param nodeStruct:
    :return:
    """
    nodes.set_val_obj(nodeStruct.o_obj.h_idObj, "h_idObj", nodeStruct.o_obj.h_idObj)
    nodes.set_val_obj(nodeStruct.o_obj.h_idObj, "h_idSubObj", nodeStruct.o_obj.h_idSubObj)
    nodes.set_val_obj(nodeStruct.o_obj.h_idObj, "i_typeData", nodeStruct.o_obj.i_typeData)
    nodes.set_val_obj(nodeStruct.o_obj.h_idObj, "d_value", nodeStruct.o_obj.d_value)
    return nodes.list_objs


def set_nodes(i_status, nodeStruct):
    """
    Сохраняет узел в краткосрочном хранилище
    :param i_status: код ошибки получения ответа, его будем ассоциировать с i_code_answer
    :return:
    """
    # global nodes
    i_append = nodes.set_val(nodeStruct.i_idNode, "i_idNode", nodeStruct.i_idNode)
    nodes.set_val(nodeStruct.i_idNode, "i_code_answer", i_status)
    nodes.set_val(nodeStruct.i_idNode, "i_codeCommand", nodeStruct.i_codeCommand)
    nodes.set_val(nodeStruct.i_idNode, "s_command", nodes.mesPacked.dict_classif[nodeStruct.i_codeCommand])
    nodes.set_val(nodeStruct.i_idNode, "s_message", nodes.mesPacked.dict_classif[i_status])
    nodes.set_val(nodeStruct.i_idNode, "Objs", loadObjs(nodeStruct))


def save_node(i_status, nodeStruct):
    """
    Функция записывает данные по узлу и объекту в краткосрочный архив
    :param i_status: код ошибки получения ответа, его будем ассоциировать с i_code_answer
    :param nodeStruct: объект с данными по узлу
    :return:
    """
    if i_status == mesPacked.OK:
        set_nodes(i_status, nodeStruct)


def run_parser(stdin, stdout):
    """
    функция обрабатывает входное сообщение от клиента и готовит ответ, при этом проверяя контрольную сумму
    пока от клиента не придет i_codeCommand=CODE_STOP
    :param stdin:
    :param stdout:
    :return:
    """
    global i_commandCode

    data = stdin.readline()
    nodeStruct = NodeInfo()
    while nodeStruct.i_codeCommand != mesPacked.CODE_EXIT:
        i_status, nodeStruct = mesPacked.recvMessageNode(data)
        if nodeStruct.i_codeCommand == mesPacked.CODE_START:
            save_node(i_status, nodeStruct)
            if i_status == mesPacked.OK:
                stdout.write(nodeStruct.o_obj.b_message)
                mesPacked.print_message("b_message:{0}".format(nodeStruct.o_obj.b_message), PLCGlobals.BREAK_DEBUG)
                data = stdin.readline()
                i_status, nodeStruct = mesPacked.recvMessageNode(data)
            else:
                pass
        if nodeStruct.i_codeCommand == mesPacked.CODE_SINGLE_START:
            save_node(i_status, nodeStruct)
            nodeStruct.i_codeCommand = mesPacked.CODE_EXIT
            if i_status == mesPacked.OK:
                stdout.write(nodeStruct.o_obj.b_message)
                mesPacked.print_message("b_message:{0}".format(nodeStruct.o_obj.b_message), PLCGlobals.BREAK_DEBUG)
            else:
                pass

        elif nodeStruct.i_codeCommand == mesPacked.CODE_LIST_NODES:
            mesPacked.print_message("Start listing nodes, recieve code:{0}...".format(nodeStruct.i_codeCommand),
                                    PLCGlobals.INFO)
            nodes.print_list_nodes()
            break
        elif nodeStruct.i_codeCommand == mesPacked.CODE_STOP:
            mesPacked.print_message("Stop recieve, recieve code:{0}...".format(nodeStruct.i_codeCommand),
                                    PLCGlobals.INFO)
            mesPacked.setCommandNodeStruct(mesPacked.CODE_STOP)
            stdout.write(nodeStruct.o_obj.b_message)
            mesPacked.print_message("b_message:{0}".format(nodeStruct.o_obj.b_message), PLCGlobals.BREAK_DEBUG)
            break
        elif nodeStruct.i_codeCommand == mesPacked.CODE_EXIT:
            mesPacked.print_message("Exit session:{0}...".format(nodeStruct.i_codeCommand), PLCGlobals.INFO)
            mesPacked.setCommandNodeStruct(mesPacked.CODE_EXIT)
            stdout.write(nodeStruct.o_obj.b_message)
            mesPacked.print_message("b_message:{0}".format(nodeStruct.o_obj.b_message), PLCGlobals.BREAK_DEBUG)
            break
        elif nodeStruct.i_codeCommand == mesPacked.CODE_EXIT_SERVER:
            mesPacked.print_message("Stop servers, recieve code:{0}...".format(nodeStruct.i_codeCommand),
                                    PLCGlobals.INFO)
            mesPacked.nodeStruct.i_codeCommand=mesPacked.CODE_EXIT_SERVER;
            i_commandCode=mesPacked.CODE_EXIT_SERVER
            break
            exit(0)
        else:
            pass

            # последнаая ответка после чего завершаем сеанс, закываем поток
            # stdout.write(nodeStruct.o_obj.b_message)
            # mesPacked.print_message("b_message:{0}".format(nodeStruct.o_obj.b_message), PLCGlobals.INFO)


main()
