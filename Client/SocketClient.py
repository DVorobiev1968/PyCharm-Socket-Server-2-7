# -*- coding: utf-8 -*-

import socket, sys

if sys.version_info < (3, 7):
    if sys.platform == "linux" or sys.platform == "linux2":
        from twisted.internet.error import ConnectionRefusedError
    elif sys.platform == "darwin":
        pass
    elif sys.platform == "win32":
        from twisted.internet.error import ConnectionRefusedError
else:
    if sys.platform == "linux" or sys.platform == "linux2":
        pass
    elif sys.platform == "darwin":
        pass
    elif sys.platform == "win32":
        pass

from Server.MesPacked import MesPacked, NodeInfo
from Server.Nodes import Nodes
from Server.PLCGlobals import PLCGlobals

class SocketClient():
    """
    класс реализует работу сетевого Python-клиента
    По умолчанию в конструкторе сипользуются следующие настройки:
        * host: localhost
        * port: 8889
    """

    def __init__(self,host="localhost",port=8889):
        self.host=host
        self.port=port
        self.mesPacked = MesPacked()
        self.nodes=Nodes()
        self.conn=None

    def set_socket_node(self,id_Node, id_Obj, i_command, d_value=0, idSubObj=0):
        """
        метод отправляет на сервер телеграмму с необходимой командой

        :param: * id_Node: идентификатор узла
                * id_Obj: идентификатор объекта
                * i_command: код команды
                * d_value: значение для записи
                * idSubObj: идентификатор субобъекта, по умолчанию

        :return: * i_status: код ошибки
                * nodeStruct: объект заполненная структура узла

        """
        i_status=0
        nodeStruct = NodeInfo()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
            self.mesPacked.print_message("set_socket_node:->:{0}".
                                    format(nodeStruct.o_obj.b_message),
                                    PLCGlobals.INFO)
            s_received = str(sock.recv(1024))
            i_status, nodeStruct = self.mesPacked.recvMessageNode(s_received)
            if (i_status == self.mesPacked.SEARCH_FAIL):
                err_msg = "set_socket_node:Err:{0}(1:<20s)".format(i_status, self.mesPacked.errMessage(i_status))
                self.mesPacked.print_message(err_msg, PLCGlobals.ERROR)
            else:
                b_message = "set_socket_node:<-:{0}".format(nodeStruct.o_obj.b_message)
                self.mesPacked.print_message(b_message, PLCGlobals.INFO)
            sock.close()


        except ConnectionRefusedError as err_message:
            self.mesPacked.print_message(err_message.strerror, PLCGlobals.ERROR)
            return 0

        except IOError as err_message:
            self.mesPacked.print_message(err_message.strerror, PLCGlobals.ERROR)
            return 0

        finally:
            def get_value():
                if i_status==self.mesPacked.OK:
                    return nodeStruct.o_obj.d_value
                else:
                    return 0
            return  get_value()

    def load_for_algoritm(self, id_Node, id_Obj, idSubObj=0):
        """
        функция отправляет на сервер телеграмму что запрошены данные для
        расчета алгоритма

        :param: * id_Node: идентификатор узла
                * id_Obj: идентификатор объекта
                * idSubObj: идентификатор субобъекта, по умолчанию =0

        :return: * i_status: код ошибки
                * nodeStruct: заполненная структура узла

        """
        try:
            i_status=self.mesPacked.SET_VAL_FAIL
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
            self.mesPacked.print_message("load_for_algoritm:->:{0}".
                                    format(nodeStruct.o_obj.b_message),
                                    PLCGlobals.INFO)

            s_received = str(sock.recv(1024))
            i_status, nodeStruct = self.mesPacked.recvMessageNode(s_received)
            if (i_status != self.mesPacked.SEARCH_FAIL):
                b_message = "load_for_algoritm:{0}".format(nodeStruct.o_Algoritm)
                self.mesPacked.print_message(b_message, PLCGlobals.INFO)
                d_value = nodeStruct.o_obj.d_value
            else:
                err_message = "load_for_algoritm:Err:{0}({1:<20s})".format(i_status, self.mesPacked.dict_classif[i_status])
                self.mesPacked.print_message(err_message, PLCGlobals.ERROR)
                d_value = 0.0
            sock.close()

        except ConnectionRefusedError as err_message:
            self.mesPacked.print_message(err_message.strerror, PLCGlobals.ERROR)
            return 0

        except IOError as err_message:
            self.mesPacked.print_message(err_message.strerror, PLCGlobals.ERROR)
            return 0

        finally:
            def get_value():
                if i_status==self.mesPacked.OK:
                    return nodeStruct.o_obj.d_value
                else:
                    return 0
            return  get_value()

    def save_for_algoritm(self, id_Node, id_Obj, d_value=0, idSubObj=0):
        """
        функция отправляет на сервер телеграмму о завершении расчета алгоритма

        :param: * id_Node: идентификатор узла
                * id_Obj: идентификатор объекта
                * idSubObj: идентификатор субобъекта, по умолчанию 0
                * d_value: значение которое было расчитано в алгоритме
        :return: * i_status: код ошибки
                * nodeStruct: заполненная структура узла
        """
        try:
            i_status=self.mesPacked.SET_VAL_FAIL
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            nodeStruct = NodeInfo()
            i_code_answer = self.mesPacked.SET_ALGORITM_VAL_OK
            nodeStruct.i_idNode = id_Node
            nodeStruct.i_code_answer = i_code_answer
            nodeStruct.i_codeCommand = self.mesPacked.CODE_SAVE_FOR_ALGORITM
            nodeStruct.s_command = self.mesPacked.dict_classif[nodeStruct.i_codeCommand]
            nodeStruct.s_message = self.mesPacked.dict_classif[i_code_answer]
            nodeStruct.o_obj.h_idObj = 0x0 + id_Obj
            nodeStruct.o_obj.h_idSubObj = 0x0 + idSubObj
            nodeStruct.o_obj.d_value=d_value
            self.mesPacked.setB_message(0, nodeStruct)
            sock.connect((self.host, self.port))
            sock.sendall(nodeStruct.o_obj.b_message)
            self.mesPacked.print_message("save_for_algoritm->:{0}".
                                    format(nodeStruct.o_obj.b_message),
                                    PLCGlobals.INFO)

            s_received = str(sock.recv(1024))
            i_status, nodeStruct = self.mesPacked.recvMessageNode(s_received)
            if (i_status != self.mesPacked.SEARCH_FAIL):
                b_message = "save_for_algoritm:{0};d_value:{1:4.6f}".format(nodeStruct.o_Algoritm,
                                                                            nodeStruct.o_obj.d_value)
                self.mesPacked.print_message(b_message, PLCGlobals.INFO)
                d_value = nodeStruct.o_obj.d_value
            else:
                err_message = "save_for_algoritm:Err:{0}({1:<20s})".format(i_status, self.mesPacked.dict_classif[i_status])
                self.mesPacked.print_message(err_message, PLCGlobals.ERROR)
                d_value = 0.0
            sock.close()

        except ConnectionRefusedError as err_message:
            self.mesPacked.print_message(err_message.strerror, PLCGlobals.ERROR)
            return 0

        except IOError as err_message:
            self.mesPacked.print_message(err_message.strerror, PLCGlobals.ERROR)
            return 0

        finally:
            def get_value():
                if i_status==self.mesPacked.OK:
                    return nodeStruct.o_obj.d_value
                else:
                    return 0
            return  get_value()

    def load_socket_node(self, id_Node, id_Obj, idSubObj=0):
        """
        метод для поиска узла и выгрузки данных

        :param: * id_Node: идентификатор узла
                * id_Obj: идентификатор объекта
                * idSubObj: идентификатор субобъекта, по умолчанию 0

        :return: * i_status: код ошибки
                * nodeStruct: заполненная структура узла
        """
        try:
            i_status=self.mesPacked.SET_VAL_FAIL
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

            s_received=sock.recv(1024)
            if sys.version_info > (3, 0):
                s_received = s_received.decode('utf-8')
            i_status, nodeStruct = self.mesPacked.recvMessageNode(s_received)
            if (i_status != self.mesPacked.SEARCH_FAIL):
                b_message = "loadSocketNode<-:{0}".format(nodeStruct.o_obj.b_message)
                self.mesPacked.print_message(b_message, PLCGlobals.INFO)
                d_value = nodeStruct.o_obj.d_value
            else:
                err_message = "loadSocketNode:Err:{0}({1:<20s})".format(i_status, self.mesPacked.dict_classif[i_status])
                self.mesPacked.print_message(err_message, PLCGlobals.ERROR)
                d_value = 0.0
            sock.close()

        except ConnectionRefusedError as err_message:
            self.mesPacked.print_message(err_message.strerror, PLCGlobals.ERROR)
            return 0

        except IOError as err_message:
            self.mesPacked.print_message(err_message.strerror, PLCGlobals.ERROR)
            return 0

        finally:
            def get_value():
                if i_status==self.mesPacked.OK:
                    return nodeStruct.o_obj.d_value
                else:
                    return 0
            return  get_value()
