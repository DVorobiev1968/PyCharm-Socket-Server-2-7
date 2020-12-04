# -*- coding: utf-8 -*-

import re, random, sys, pickle

from numpy.core import double

from switch import switch
from PLCGlobals import PLCGlobals
from NodeInfo import NodeInfo

class MesPacked():
    def __init__(self):
        self.code_status=0
        self.errMessage=str("")
        # коды i_code_answer и их описание
        self.CODE_NODES_OPERATION = 60
        self.ADD_OK = self.CODE_NODES_OPERATION+PLCGlobals.ADD_OK
        self.ADD_FAIL = self.CODE_NODES_OPERATION+PLCGlobals.ADD_FAIL
        self.UPDATE_OK = self.CODE_NODES_OPERATION+PLCGlobals.UPDATE_OK
        self.UPDATE_FAIL = self.CODE_NODES_OPERATION+PLCGlobals.UPDATE_FAIL
        self.SET_VAL_OK = self.CODE_NODES_OPERATION+PLCGlobals.SET_VAL_OK
        self.SET_VAL_FAIL = self.CODE_NODES_OPERATION+PLCGlobals.SET_VAL_FAIL
        self.SEARCH_FAIL = 78
        self.SEARCH_OK = 79
        self.OK = 80
        self.ERR = 99
        self.SYNTAX_ERR = 101
        # коды команд
        self.CODE_START = 1
        self.CODE_STOP = 2
        self.CODE_SINGLE_START = 3
        self.CODE_LIST_NODES = 10
        self.CODE_FIND_NODES = 11
        self.CODE_EXIT = 20
        self.CODE_EXIT_SERVER = 21
        # сетевые настройки
        self.port = 8889
        self.dict_typeData = {
            "None": -1,
            "Boolean": 0,
            "Integer": 1,
            "Float": 2,
            "Double": 3,
            "String": 4,
            "Dict": 5,
            "Bytes": 6,
            "Object": 7
        }
        self.dict_classif = {
            self.OK: "Command completed completely",
            self.CODE_START: "Start command",
            self.CODE_STOP: "Stop command",
            self.CODE_SINGLE_START: "Single start command",
            self.CODE_LIST_NODES: "Printing nodes list",
            self.CODE_FIND_NODES: "Search nodes and objext",
            self.CODE_EXIT: "Close connect Client stopped",
            self.CODE_EXIT_SERVER: "Close connect Server stopped",
            self.CODE_NODES_OPERATION: "Codes Error/Info for node and object",
            self.SEARCH_OK: "Node and object found OK",
            self.SEARCH_FAIL: "Node and object not found",
            self.ADD_OK: "Add list_node/list_obj it`s OK",
            self.ADD_FAIL: "Add list_node/list_obj it`s FAIL",
            self.UPDATE_OK: "Update list_node/list_obj  it`s OK",
            self.UPDATE_FAIL: "Update list_node/list_obj it`s FAIL",
            self.SET_VAL_OK: "Set list_node/list_obj it`s OK",
            self.SET_VAL_FAIL:"Set list_node/list_obj it`s FAIL",
            self.ERR: "General error",
            100: "Request not supported.",
            self.SYNTAX_ERR: "Syntax error.",
            102: "Request not processed due to internal state.",
            103: "Time-out (where applicable).",
            104: "No default net set.",
            105: "No default node set.",
            106: "Unsupported net.",
            107: "Unsupported node.",
            200: "Lost guarding message.",
            201: "Lost connection.",
            202: "Heartbeat started.",
            203: "Heartbeat lost.",
            204: "Wrong NMT state.",
            205: "Boot-up.",
            300: "Error passive.",
            301: "Bus off.",
            303: "CAN buffer overflow.",
            304: "CAN init.",
            305: "CAN active (at init or start-up).",
            400: "PDO already used.",
            401: "PDO length exceeded.",
            501: "LSS implementation- / manufacturer-specific error.",
            502: "LSS node-ID not supported.",
            503: "LSS bit-rate not supported.",
            504: "LSS parameter storing failed.",
            505: "LSS command failed because of media error.",
            600: "Running out of memory.",
            0x00000000: "No abort.",
            0x05030000: "Toggle bit not altered.",
            0x05040000: "SDO protocol timed out.",
            0x05040001: "Command specifier not valid or unknown.",
            0x05040002: "Invalid block size in block mode.",
            0x05040003: "Invalid sequence number in block mode.",
            0x05040004: "CRC error (block mode only).",
            0x05040005: "Out of memory.",
            0x06010000: "Unsupported access to an object.",
            0x06010001: "Attempt to read a write only object.",
            0x06010002: "Attempt to write a read only object.",
            0x06020000: "Object does not exist.",
            0x06040041: "Object cannot be mapped to the PDO.",
            0x06040042: "Number and length of object to be mapped exceeds PDO length.",
            0x06040043: "General parameter incompatibility reasons.",
            0x06040047: "General internal incompatibility in device.",
            0x06060000: "Access failed due to hardware error.",
            0x06070010: "Data type does not match: length of service parameter does not match.",
            0x06070012: "Data type does not match: length of service parameter too high.",
            0x06070013: "Data type does not match: length of service parameter too short.",
            0x06090011: "Sub index does not exist.",
            0x06090030: "Invalid value for parameter (download only).",
            0x06090031: "Value range of parameter written too high.",
            0x06090032: "Value range of parameter written too low.",
            0x06090036: "Maximum value is less than minimum value.",
            0x060A0023: "Resource not available: SDO connection.",
            0x08000000: "General error.",
            0x08000020: "Data cannot be transferred or stored to application.",
            0x08000021: "Data cannot be transferred or stored to application because of local control.",
            0x08000022: "Data cannot be transferred or stored to application because of present device state.",
            0x08000023: "Object dictionary not present or dynamic generation fails.",
            0x08000024: "No data available."}

        self.nodeStruct=NodeInfo()                       # переменная узел

    def print_message(self, messageErr, key):
        if PLCGlobals.debug <= key:
            print '{:1d}:{:<40s}'.format(key,messageErr)
            sys.stdout.flush()

    def initNodeStruct(self, id_node, idObj, idSubObj, d_value):
        """
        метод для отладки инициализирует переменную
        содержащую структуру узла, с описанием объектов
        внутри применяется только для отладки, в рабочем режиме
        nodeStruct заполняется при получении данных от клиента
        :param id_node:
        :param idObj:
        :param idSubObj:
        :param d_value:
        :return: объект типа nodeStruct
        """
        nodeStruct = NodeInfo()  # переменная узел
        nodeStruct.i_idNode=id_node
        # код команды присваивается в зависимости от протокола работы узла
        nodeStruct.i_codeCommand = self.CODE_START
        # описание команды
        nodeStruct.s_command = self.dict_classif[self.nodeStruct.i_codeCommand]
        # строка получаемая из буфера
        nodeStruct.s_message = self.dict_classif[self.nodeStruct.i_codeCommand]
        nodeStruct.o_obj.h_idObj=0x0+idObj
        nodeStruct.o_obj.h_idSubObj=0x0+idSubObj
        nodeStruct.o_obj.i_typeData=self.dict_typeData["Double"]
        nodeStruct.o_obj.d_value=d_value
        return nodeStruct

    def setCommandNodeStruct(self, i_command,i_code_answer=0, id_node=0, idObj=0, idSubObj=0, d_value=0):
        """
        метод для отладки инициализирует переменную
        содержащую структуру узла, с описанием объектов
        внутри применяется только для отладки, в рабочем режиме
        nodeStruct заполняется при получении данных от клиента
        :param i_command: код команды
        :param i_code_answer: код ответа на команду (статут)
        :param id_node: идентификатор узла
        :param idObj: идентификатор объекта
        :param idSubObj: идентификатор субобъекта
        :param d_value: значение

        :return: объект типа nodeStruct
        """
        nodeStruct = NodeInfo()  # переменная узел
        nodeStruct.i_idNode=id_node
        # код команды присваивается в зависимости от протокола работы узла
        nodeStruct.i_codeCommand = i_command
        # описание команды
        nodeStruct.s_command = self.dict_classif[self.nodeStruct.i_codeCommand]
        # строка получаемая из буфера
        nodeStruct.s_message = self.dict_classif[self.nodeStruct.i_codeCommand]
        # статус ответа OK
        if (i_code_answer==0):
            nodeStruct.i_code_answer=self.OK
        else:
            nodeStruct.i_code_answer=i_code_answer

        nodeStruct.o_obj.h_idObj=0x0+idObj
        nodeStruct.o_obj.h_idSubObj=0x0+idSubObj
        nodeStruct.o_obj.i_typeData=self.dict_typeData["Double"]
        nodeStruct.o_obj.d_value=d_value
        return nodeStruct

    def setB_message(self, code_err=0, nodeStruct=NodeInfo()):
        """
        метод подготовливает 2 строки для сериализации:
        1. b_message- упрощеная строка содержит информмацию из строкового представления
        2. b_obj - расширенная непосредственно объект для сериализауии
        :param code_err:
        :param nodeStruct:
        :return:
        """
        i_length = 0
        if code_err==0:
            code_err=nodeStruct.i_code_answer
        nodeStruct.o_obj.b_message = bytes("{0};{1};{2};{3};{4};{5};{6}".format(
            nodeStruct.i_idNode,
            nodeStruct.i_codeCommand,
            code_err,
            nodeStruct.o_obj.h_idObj,
            nodeStruct.o_obj.h_idSubObj,
            nodeStruct.o_obj.i_typeData,
            nodeStruct.o_obj.d_value))
        i_length = len(nodeStruct.o_obj.b_message)
        i_length+=3+2
        nodeStruct.o_obj.b_message = bytes("{0};{1}\r\n".format(nodeStruct.o_obj.b_message, i_length))
        nodeStruct.o_obj.b_obj=pickle.dumps(nodeStruct,0)
        i_length_obj=len(nodeStruct.o_obj.b_obj)
        return i_length,nodeStruct

    def set_CRC(self,nodeStruct):
        """
        метод расчитывает котрольную сумму по b_message
        :param nodeStruct:
        :return:
        """
        i_crc=0
        for i in range (len(nodeStruct.o_obj.b_message)):
            i_crc+=len(nodeStruct.o_obj.b_message[i])
        return i_crc

    def set_CRC_b_obj(self,nodeStruct):
        """
        метод расчитывает котрольную сумму по b_obj
        :param nodeStruct:
        :return:
        """
        i_crc=0
        for i in range (len(nodeStruct.o_obj.b_obj)):
            i_crc+=len(nodeStruct.o_obj.b_obj[i])
        return i_crc

    def sendMessage(self, i_data, nodeStruct):
        """
         Читаем св-ва класса и дополняем кодом ответа
        :return:
        """
        i_status = self.OK
        i_length=0
        b_message=bytes()
        b_obj=bytes()
        if i_data == nodeStruct.o_obj.i_check:
            if nodeStruct.i_codeCommand == self.CODE_START:
                i_length, nodeStruct = self.setB_message(self.OK, nodeStruct)
                i_status = self.OK
            elif nodeStruct.i_codeCommand == self.CODE_SINGLE_START:
                i_length, nodeStruct = self.setB_message(self.OK, nodeStruct)
                i_status = self.OK
            elif nodeStruct.i_codeCommand == self.CODE_STOP:
                i_length, nodeStruct = self.setB_message(self.OK,nodeStruct)
                i_status = self.OK
        else:
            i_length, nodeStruct = self.setB_message(self.ERR,nodeStruct)
            i_status = self.ERR

        return i_status, i_length, nodeStruct

    def recvMessage(self, data, nodeStruct):
        """
        Метод принимает строку байт от клиента и проверяет на целостность данных
        :param data: байтовая строка
        :nodeStruct: объект nodeStruct
        :return: код ошибки, обработанный объект nodeStruct
        """
        if len(data)>1:
            i_status = self.OK
            parse_str = re.split("[;\r\n]", data)
            i_data = len(data)
            nodeStruct=self.readData(parse_str, nodeStruct)
            nodeStruct.s_message = "{0}:{1:d}:{2}".format(object.__name__, nodeStruct.o_obj.i_check, parse_str)
            self.print_message(nodeStruct.s_message, PLCGlobals.INFO)
            i_status, \
            i_length, \
            nodeStruct = self.sendMessage(i_data, nodeStruct)
            return i_status, nodeStruct
        else:
            return self.SEARCH_FAIL, NodeInfo()

    def recvMessageNode(self, data):
        """
        Метод принимает строку байт от клиента и проверяет на целостность данных
        :param data: байтовая строка
        :return: код ошибки, nodeStruct
        """
        if len(data)>1:
            i_status = self.OK
            parse_str = re.split("[;\r\n]", data)
            i_data = len(data)
            nodeStruct=self.readDataNodeStruct(parse_str)
            self.errMessage = "{0}:{1:d}:{2}".format(object.__name__,
                                                          nodeStruct.o_obj.i_check,
                                                          parse_str)
            self.print_message(self.errMessage, PLCGlobals.INFO)
            i_status, \
            i_length, \
            self.nodeStruct = self.sendMessage(i_data,nodeStruct)

            return i_status, nodeStruct
        else:
            return self.SEARCH_FAIL, NodeInfo()

    def setValue(self, strValue, nodeStruct):
        """
           Метод проверяет тип данных значения и устанавливает соответсвующий тип данных
           :param strValue: строка для парсера
           :return: nodeStruct
           """
        i_status = self.OK
        if isinstance(strValue, int):
            nodeStruct.o_obj.i_typeData = self.dict_typeData["Integer"]
            nodeStruct.o_obj.d_value = int(strValue)
        elif isinstance(strValue, float):
            nodeStruct.o_obj.i_typeData = self.dict_typeData["Float"]
            nodeStruct.o_obj.d_value = float(strValue)
        elif isinstance(strValue, bool):
            nodeStruct.o_obj.i_typeData = self.dict_typeData["Boolean"]
            nodeStruct.o_obj.d_value = bool(strValue)
        elif isinstance(strValue, dict):
            nodeStruct.o_obj.i_typeData = self.dict_typeData["Dict"]
            nodeStruct.o_obj.d_value = dict()
        elif isinstance(strValue, str):
            nodeStruct.o_obj.i_typeData = self.dict_typeData["Double"]
            nodeStruct.o_obj.d_value = double(strValue.replace(',', '.'))
        else:
            nodeStruct.o_obj.i_typeData = self.dict_typeData["Object"]
            nodeStruct.o_obj.d_value = bytearray(strValue, "utf-8")

        return nodeStruct

    def setValueNodeStruct(self, strValue):
        """
           Метод проверяет тип данных значения и устанавливает соответсвующий тип данных
           :param strValue: строка для парсера
           :return:i_typeData, d_value
           """
        i_typeData=0
        d_value=0
        if isinstance(strValue, int):
            i_typeData = self.dict_typeData["Integer"]
            d_value = int(strValue)
        elif isinstance(strValue, float):
            i_typeData = self.dict_typeData["Float"]
            d_value = float(strValue)
        elif isinstance(strValue, bool):
            i_typeData = self.dict_typeData["Boolean"]
            d_value = bool(strValue)
        elif isinstance(strValue, dict):
            i_typeData = self.dict_typeData["Dict"]
            d_value = dict()
        elif isinstance(strValue, str):
            i_typeData = self.dict_typeData["Double"]
            d_value = double(strValue.replace(',', '.'))
        else:
            i_typeData = self.dict_typeData["Object"]
            d_value = bytearray(strValue, "utf-8")

        return i_typeData, d_value

    def setD_value(self, nodeStruct, d_value=0):
        """
        метод устанавливает значение d_value, используется для отладки
        d_value необязательный аргумент, если не указывается то присваивается
        случайным образом в диапазоне 0-1
        :param nodeStruct:
        :param d_value:
        :return:
        """
        if d_value == 0:
            nodeStruct.o_obj.d_value *= random.random()
        else:
            nodeStruct.o_obj.d_value=d_value
        return nodeStruct

    def readData(self, stringData, nodeStruct):
        """
        Метод парсит телеграмму от клиента раскладывает ее в поля
        :param stringData: в соответствии с принятым соглашением по телеграмме
        :nodeStruct:
        :return: i_status, nodeStruct
        """
        length = len(stringData)
        for i in range(length - 2):
            for case in switch(i):
                if case(0):
                    nodeStruct.i_idNode = int(stringData[i])
                    break
                if case(1):
                    nodeStruct.i_codeCommand = int(stringData[i])
                    break
                if case(2):
                    nodeStruct.i_code_answer = int(stringData[i])
                    break
                if case(3):
                    nodeStruct.o_obj.h_idObj = int(stringData[i])
                    break
                if case(4):
                    nodeStruct.o_obj.h_idSubObj = int(stringData[i])
                    break
                if case(5):
                    break
                if case(6):
                    nodeStruct=self.setValue(stringData[i],nodeStruct)
                    # для отладки после убрать, поскольку запускаем без параметр, будет проставляться random()
                    # nodeStruct=self.setD_value(nodeStruct)
                    break
                if case(length - 3):
                    nodeStruct.o_obj.i_check = int(stringData[i])
                    break
                if case():
                    break
        return nodeStruct

    def readDataNodeStruct(self, stringData):
        """
        Метод парсит телеграмму от клиента раскладывает ее в поля
        данные записываются в переменную nodeStruct, содержащую строктуру узла и объекта
        :param stringData: в соответствии с принятым соглашением по телеграмме
        :return:nodeStruct
        """
        i_status = self.OK
        length = len(stringData)
        nodeStruct=NodeInfo()
        for i in range(length - 2):
            for case in switch(i):
                if case(0):
                    nodeStruct.i_idNode = int(stringData[i])
                    break
                if case(1):
                    nodeStruct.i_codeCommand = int(stringData[i])
                    break
                if case(2):
                    nodeStruct.i_code_answer = int(stringData[i])
                    break
                if case(3):
                    nodeStruct.o_obj.h_idObj = int(stringData[i])
                    break
                if case(4):
                    nodeStruct.o_obj.h_idSubObj = int(stringData[i])
                    break
                if case(5):
                    # nodeStruct.o_obj.i_typeData = int(stringData[i])
                    break
                if case(6):
                    nodeStruct.o_obj.i_typeData, \
                    nodeStruct.o_obj.d_value = self.setValueNodeStruct(stringData[i])
                    break
                if case(length - 3):
                    nodeStruct.o_obj.i_check = int(stringData[i])
                    break
                if case():
                    break
        return nodeStruct