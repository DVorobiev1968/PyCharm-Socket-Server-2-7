# -*- coding: utf-8 -*-

import socket

from MesPacked import MesPacked, NodeInfo
from Nodes import Nodes
from PLCGlobals import PLCGlobals

class SocketClient():
    def __init__(self,host="localhost",port="8889"):
        """
        По умолчанию localhost, port:8889
        :rtype: object
        """
        self.host=host
        self.port=port
        self.mesPacked = MesPacked()
        self.nodes=Nodes()
        self.conn=None

    def set_socket_node(self,id_Node, id_Obj, i_command, d_value=0, idSubObj=0):
        """
        функция отправляет на сервер телеграмму с необходимой командой
        :param id_Node: идентификатор узла
        :param id_Obj: идентификатор объекта
        :param i_command: код команды
        :param d_value: значение для записи
        :param idSubObj: идентификатор субобъекта, по умолчанию
        :return:
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            nodeStruct = NodeInfo()
            i_code_answer = 0
            nodeStruct.i_idNode = id_Node
            nodeStruct.i_code_answer = i_code_answer
            nodeStruct.i_codeCommand = i_command
            nodeStruct.s_command = self.mesPacked.dict_classif[i_command]
            nodeStruct.s_message = self.mesPacked.dict_classif[i_code_answer]
            nodeStruct.o_obj.h_idObj = 0x0 + id_Obj
            nodeStruct.o_obj.h_idSubObj = 0x0 + idSubObj
            nodeStruct.o_obj.d_value = d_value
            self.mesPacked.setB_message(0, nodeStruct)
            sock.connect((self.host,self.port))
            sock.sendall(nodeStruct.o_obj.b_message)
            self.mesPacked.print_message("sendall: b_message:{0}".
                                    format(nodeStruct.o_obj.b_message),
                                    PLCGlobals.INFO)
            s_received = str(sock.recv(1024))
            i_status, nodeStruct = self.mesPacked.recvMessageNode(s_received)
            if (i_status == self.mesPacked.SEARCH_FAIL):
                err_msg = "Error:{0}(1:<20s)".format(i_status, self.mesPacked.errMessage(i_status))
                self.mesPacked.print_message(err_msg, PLCGlobals.ERROR)
            else:
                b_message = "recvMessageNodes: b_message:{0}".format(nodeStruct.o_obj.b_message)
                self.mesPacked.print_message(b_message, PLCGlobals.INFO)
            sock.close()
        except ConnectionRefusedError as err_message:
            self.mesPacked.print_message(err_message.strerror, PLCGlobals.ERROR)


    def load_for_algoritm(self, id_Node, id_Obj, idSubObj=0):
        """
        функция отправляет на сервер телеграмму что запрошены данные для
         расчета алгоритма
        :param id_Node: идентификатор узла
        :param id_Obj: идентификатор объекта
        :param idSubObj: идентификатор субобъекта, по умолчанию 0
        :return:
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            nodeStruct = NodeInfo()
            i_code_answer = self.mesPacked.SET_ALGORITM_WAIT
            nodeStruct.i_idNode = id_Node
            nodeStruct.i_code_answer = i_code_answer
            nodeStruct.i_codeCommand = self.mesPacked.CODE_LOAD_FOR_ALGORITM
            nodeStruct.s_command = self.mesPacked.dict_classif[nodeStruct.i_codeCommand]
            nodeStruct.s_message = self.mesPacked.dict_classif[i_code_answer]
            nodeStruct.o_obj.h_idObj = 0x0 + id_Obj
            nodeStruct.o_obj.h_idSubObj = 0x0 + idSubObj
            self.mesPacked.setB_message(0, nodeStruct)
            sock.connect((self.host, self.port))
            sock.sendall(nodeStruct.o_obj.b_message)
            self.mesPacked.print_message("sendall: b_message:{0}".
                                    format(nodeStruct.o_obj.b_message),
                                    PLCGlobals.INFO)

            s_received = str(sock.recv(1024))
            i_status, nodeStruct = self.mesPacked.recvMessageNode(s_received)
            if (i_status != self.mesPacked.SEARCH_FAIL):
                b_message = "loadSocketNode:{0}".format(nodeStruct.o_obj.b_message)
                self.mesPacked.print_message(b_message, PLCGlobals.INFO)
                d_value = nodeStruct.o_obj.d_value
            else:
                err_message = "Err:{0}({1:<20s})".format(i_status, self.mesPacked.dict_classif[i_status])
                self.mesPacked.print_message(err_message, PLCGlobals.INFO)
                d_value = 0.0
            sock.close()

        except ConnectionRefusedError as err_message:
            self.mesPacked.print_message(err_message.strerror, PLCGlobals.ERROR)
            return 0
        return d_value


    def load_socket_node(self, id_Node, id_Obj, idSubObj=0):
        """
        функция отправляет на сервер телеграмму с необходимой командой
        :param id_Node: идентификатор узла
        :param id_Obj: идентификатор объекта
        :param idSubObj: идентификатор субобъекта, по умолчанию 0
        :return:
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            nodeStruct = NodeInfo()
            i_code_answer = 0
            nodeStruct.i_idNode = id_Node
            nodeStruct.i_code_answer = i_code_answer
            nodeStruct.i_codeCommand = self.mesPacked.CODE_FIND_NODES
            nodeStruct.s_command = self.mesPacked.dict_classif[self.mesPacked.CODE_FIND_NODES]
            nodeStruct.s_message = self.mesPacked.dict_classif[i_code_answer]
            nodeStruct.o_obj.h_idObj = 0x0 + id_Obj
            nodeStruct.o_obj.h_idSubObj = 0x0 + idSubObj
            self.mesPacked.setB_message(0, nodeStruct)
            sock.connect((self.host, self.port))
            sock.sendall(nodeStruct.o_obj.b_message)
            self.mesPacked.print_message("sendall: b_message:{0}".
                                    format(nodeStruct.o_obj.b_message),
                                    PLCGlobals.INFO)

            b_received=sock.recv(1024)
            s_received = b_received.decode('utf-8')
            i_status, nodeStruct = self.mesPacked.recvMessageNode(s_received)
            if (i_status != self.mesPacked.SEARCH_FAIL):
                b_message = "loadSocketNode:{0}".format(nodeStruct.o_obj.b_message)
                self.mesPacked.print_message(b_message, PLCGlobals.INFO)
                d_value = nodeStruct.o_obj.d_value
            else:
                err_message = "Err:{0}({1:<20s})".format(i_status, self.mesPacked.dict_classif[i_status])
                self.mesPacked.print_message(err_message, PLCGlobals.INFO)
                d_value = 0.0
            sock.close()

        except ConnectionRefusedError as err_message:
            self.mesPacked.print_message(err_message.strerror, PLCGlobals.ERROR)
            return 0
        return d_value