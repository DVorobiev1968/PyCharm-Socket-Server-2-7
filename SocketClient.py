# -*- coding: utf-8 -*-

import socket

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

def set_socket_node(id_Node, id_Obj, i_command, d_value=0, idSubObj=0, host="", port=0):
    """
    функция отправляет на сервер телеграмму с необходимой командой
    :param id_Node: идентификатор узла
    :param id_Obj: идентификатор объекта
    :param i_command: код команды
    :param d_value: значение для записи
    :param idSubObj: идентификатор субобъекта, по умолчанию
    :param host: задаем пустую строку, чтобы использовать значение по умолчанию localhost
    :param port: задаем 0, чтобы использовать значение по умолчанию 8889
    :return:
    """
    global mesPacked
    if len(host)<1:
        host = loadSettings(1, mesPacked)
    if port<1:
        port = loadSettings(2, mesPacked)
    sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    nodeStruct = NodeInfo()
    i_code_answer=0
    nodeStruct.i_idNode=id_Node
    nodeStruct.i_code_answer=i_code_answer
    nodeStruct.i_codeCommand=i_command
    nodeStruct.s_command=mesPacked.dict_classif[i_command]
    nodeStruct.s_message=mesPacked.dict_classif[i_code_answer]
    nodeStruct.o_obj.h_idObj=0x0+id_Obj
    nodeStruct.o_obj.h_idSubObj=0x0+idSubObj
    nodeStruct.o_obj.d_value=d_value
    mesPacked.setB_message(0,nodeStruct)
    sock.connect((host, port))
    sock.sendall(bytes(nodeStruct.o_obj.b_message))
    mesPacked.print_message("sendall: b_message:{0}".
                            format(nodeStruct.o_obj.b_message),
                            PLCGlobals.INFO)
    s_received = str(sock.recv(1024))
    i_status, nodeStruct = mesPacked.recvMessageNode(s_received)
    if (i_status==mesPacked.SEARCH_FAIL):
        err_msg="Error:{0}(1:<20s)".format(i_status,mesPacked.errMessage(i_status))
        mesPacked.print_message(err_msg,PLCGlobals.ERROR)
    else:
        b_message="recvMessageNodes: b_message:{0}".format(nodeStruct.o_obj.b_message)
        mesPacked.print_message(b_message,PLCGlobals.INFO)
    sock.close()

def load_for_algoritm(id_Node, id_Obj, idSubObj=0, host="", port=0):
    """
    функция отправляет на сервер телеграмму что запрошены данные для
     расчета алгоритма
    :param id_Node: идентификатор узла
    :param id_Obj: идентификатор объекта
    :param idSubObj: идентификатор субобъекта, по умолчанию 0
    :param host: задаем пустую строку, чтобы использовать значение по умолчанию localhost
    :param port: задаем 0, чтобы использовать значение по умолчанию 8889
    :return:
    """
    global mesPacked

    if len(host)<1:
        host = loadSettings(1, mesPacked)
    if port<1:
        port = loadSettings(2, mesPacked)
    sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    nodeStruct = NodeInfo()
    i_code_answer=mesPacked.SET_ALGORITM_WAIT
    nodeStruct.i_idNode=id_Node
    nodeStruct.i_code_answer=i_code_answer
    nodeStruct.i_codeCommand=mesPacked.CODE_LOAD_FOR_ALGORITM
    nodeStruct.s_command=mesPacked.dict_classif[nodeStruct.i_codeCommand]
    nodeStruct.s_message=mesPacked.dict_classif[i_code_answer]
    nodeStruct.o_obj.h_idObj=0x0+id_Obj
    nodeStruct.o_obj.h_idSubObj=0x0+idSubObj
    mesPacked.setB_message(0,nodeStruct)
    sock.connect((host, port))
    sock.sendall(bytes(nodeStruct.o_obj.b_message))
    mesPacked.print_message("sendall: b_message:{0}".
                            format(nodeStruct.o_obj.b_message),
                            PLCGlobals.INFO)

    s_received = str(sock.recv(1024))
    i_status, nodeStruct = mesPacked.recvMessageNode(s_received)
    if (i_status!=mesPacked.SEARCH_FAIL):
        b_message="loadSocketNode:{0}".format(nodeStruct.o_obj.b_message)
        mesPacked.print_message(b_message,PLCGlobals.INFO)
        d_value=nodeStruct.o_obj.d_value
    else:
        err_message="Err:{0}({1:<20s})".format(i_status,mesPacked.dict_classif[i_status])
        mesPacked.print_message(err_message,PLCGlobals.INFO)
        d_value=0.0
    sock.close()
    return d_value

def load_socket_node(id_Node, id_Obj, idSubObj=0, host="", port=0):
    """
    функция отправляет на сервер телеграмму с необходимой командой
    :param id_Node: идентификатор узла
    :param id_Obj: идентификатор объекта
    :param idSubObj: идентификатор субобъекта, по умолчанию 0
    :param host: задаем пустую строку, чтобы использовать значение по умолчанию localhost
    :param port: задаем 0, чтобы использовать значение по умолчанию 8889
    :return:
    """
    global mesPacked

    if len(host)<1:
        host = loadSettings(1, mesPacked)
    if port<1:
        port = loadSettings(2, mesPacked)
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
    sock.connect((host, port))
    sock.sendall(bytes(nodeStruct.o_obj.b_message))
    mesPacked.print_message("sendall: b_message:{0}".
                            format(nodeStruct.o_obj.b_message),
                            PLCGlobals.INFO)

    s_received = str(sock.recv(1024))
    i_status, nodeStruct = mesPacked.recvMessageNode(s_received)
    if (i_status!=mesPacked.SEARCH_FAIL):
        b_message="loadSocketNode:{0}".format(nodeStruct.o_obj.b_message)
        mesPacked.print_message(b_message,PLCGlobals.INFO)
        d_value=nodeStruct.o_obj.d_value
    else:
        err_message="Err:{0}({1:<20s})".format(i_status,mesPacked.dict_classif[i_status])
        mesPacked.print_message(err_message,PLCGlobals.INFO)
        d_value=0.0
    sock.close()
    return d_value

##############################################################
def main():
    global mesPacked, nodes, conn
    mesPacked = MesPacked()
    nodes=Nodes()
    conn=None

    host = loadSettings(1, mesPacked)
    port = loadSettings(2, mesPacked)

    d_value_1=load_for_algoritm(1, 0x1000+7)
    d_value=load_socket_node(2, 0x1000+7)
    mesPacked.print_message("d_value:{0:4.10f}".format(d_value), PLCGlobals.INFO)
    mesPacked.print_message("d_value_1:{0:4.10f}".format(d_value_1), PLCGlobals.INFO)
    set_socket_node(5,0x1000+8,mesPacked.CODE_SINGLE_START,1968)

main()