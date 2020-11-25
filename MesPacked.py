# -*- coding: utf-8 -*-

import re, random, sys, pickle

from switch import switch
from PLCGlobals import PLCGlobals

class NodeObjInfo():
    def __init__(self):
        # атрибуты(св-ва) класса
        self.h_idObj = 0x1         # идентификатор объекта
        self.h_idSubObj = 0x100    # идентификатор субобъекта
        self.i_typeData = 0        # тип данных объекта
        self.d_value = 0.1         # возвращаемое значение
        self.i_check = 0           # контрольная сумма
        self.b_message = bytes()   # массив байт отправляемый клиенту
        self.b_obj=bytes()         # дополнительный объект для сериализации

class NodeInfo():
    def __init__(self):
        # атрибуты(св-ва) класса
        self.i_idNode = 1       # идентификатор узла
        self.i_code_answer = 0  # код ответа от узла
        self.i_codeCommand = 0  # код команды присваивается в зависимости от протокола работы узла
        self.s_command = ""     # описание команды
        self.s_message = ""     # строка получаемая из буфера
        self.o_obj=NodeObjInfo()

class MesPacked():
    def __init__(self):
        self.code_status=0
        self.errMessage=str("")
        # коды ошибок и их описание
        self.OK = 80
        self.ERR = 99
        self.SYNTAX_ERR = 101
        # коды команд
        self.CODE_START = 1
        self.CODE_STOP = 2
        self.CODE_LIST_NODES = 10
        self.CODE_EXIT = 20
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
            self.CODE_LIST_NODES: "Printing nodes list",
            self.CODE_EXIT: "Close connect Client stopped",
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
        nodeStruct заполнеятся при получении даннх от клиента
        :return:
        """
        self.nodeStruct.i_idNode=id_node
        # код команды присваивается в зависимости от протокола работы узла
        self.nodeStruct.i_codeCommand = self.CODE_START
        # описание команды
        self.nodeStruct.s_command = self.dict_classif[self.nodeStruct.i_codeCommand]
        # строка получаемая из буфера
        self.nodeStruct.s_message = self.dict_classif[self.nodeStruct.i_codeCommand]
        self.nodeStruct.o_obj.h_idObj=0x0+idObj
        self.nodeStruct.o_obj.h_idSubObj=0x0+idSubObj
        self.nodeStruct.o_obj.i_typeData=self.dict_typeData["Float"]
        self.nodeStruct.o_obj.d_value=d_value

    def setB_message(self, code_err=0, nodeStruct=NodeInfo()):
        """
        метод подготовливает 2 строки для сериализации:
        1. b_message- упрощеная строка содержит информмацию из строкового представления
        2. b_obj - расширенная непосредственно объект
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
        # return i_length,nodeStruct.o_obj.b_message,nodeStruct.o_obj.b_obj
        return i_length,nodeStruct

    def set_CRC(self):
        i_crc=0
        for i in range (len(self.nodeStruct.o_obj.b_message)):
            i_crc+=len(self.nodeStruct.o_obj.b_message[i])
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
            elif nodeStruct.i_codeCommand == self.CODE_STOP:
                i_length, nodeStruct = self.setB_message(self.OK,nodeStruct)
                i_status = self.OK
        else:
            i_length, nodeStruct = self.setB_message(self.ERR,nodeStruct)
            i_status = self.ERR

        return i_status, i_length, nodeStruct

    def recvMessage(self, data):
        """
        Метод принимает строку байт от клиента и проверяет на целостность данных
        :param data: байтовая строка
        :return: код ошибки
        """
        i_status = self.OK
        parse_str = re.split("[;\r\n]", data)
        i_data = len(data)
        self.readData(parse_str)
        self.nodeStruct.s_message = "{0}:{1:d}:{2}".format(object.__name__, self.nodeStruct.o_obj.i_check, parse_str)
        self.print_message(self.nodeStruct.s_message, PLCGlobals.INFO)
        i_status, \
        i_length, \
        self.nodeStruct = self.sendMessage(i_data,self.nodeStruct)
        return i_status

    def recvMessageNode(self, data):
        """
        Метод принимает строку байт от клиента и проверяет на целостность данных
        :param data: байтовая строка
        :return: код ошибки, nodeStruct
        """
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

    def setValue(self, strValue):
        """
           Метод проверяет тип данных значения и устанавливает соответсвующий тип данных
           :param strValue: строка для парсера
           :return:
           """
        i_status = self.OK
        if isinstance(strValue, int):
            self.nodeStruct.o_obj.i_typeData = self.dict_typeData["Integer"]
            self.nodeStruct.o_obj.d_value = int(strValue)
        elif isinstance(strValue, float):
            self.nodeStruct.o_obj.i_typeData = self.dict_typeData["Float"]
            self.nodeStruct.o_obj.d_value = float(strValue)
        elif isinstance(strValue, bool):
            self.nodeStruct.o_obj.i_typeData = self.dict_typeData["Boolean"]
            self.nodeStruct.o_obj.d_value = bool(strValue)
        elif isinstance(strValue, dict):
            self.nodeStruct.o_obj.i_typeData = self.dict_typeData["Dict"]
            self.nodeStruct.o_obj.d_value = dict()
        elif isinstance(strValue, str):
            self.nodeStruct.o_obj.i_typeData = self.dict_typeData["Float"]
            self.nodeStruct.o_obj.d_value = float(strValue.replace(',', '.'))
        else:
            self.nodeStruct.o_obj.i_typeData = self.dict_typeData["Object"]
            self.nodeStruct.o_obj.d_value = bytearray(strValue, "utf-8")

        return i_status

    def setValueNodeStruct(self, strValue):
        """
           Метод проверяет тип данных значения и устанавливает соответсвующий тип данных
           :param strValue: строка для парсера
           :return:i_typeData, d_value
           """
        i_status = self.OK
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
            i_typeData = self.dict_typeData["Float"]
            d_value = float(strValue.replace(',', '.'))
        else:
            i_typeData = self.dict_typeData["Object"]
            d_value = bytearray(strValue, "utf-8")

        return i_typeData, d_value

    def setD_value(self, d_value=0):
        if d_value == 0:
            self.nodeStruct.o_obj.d_value *= random.random()
        else:
            self.nodeStruct.o_obj.d_value=d_value
            self.nodeStruct.o_obj.d_value=self.nodeStruct.o_obj.d_value

    def readData(self, stringData):
        """
        Метод парсит телеграмму от клиента раскладывает ее в поля
        :param stringData: в соответствии с принятым соглашением по телеграмме
        :return: i_status
        """
        i_status = self.OK
        length = len(stringData)
        for i in range(length - 2):
            for case in switch(i):
                if case(0):
                    self.nodeStruct.i_idNode = int(stringData[i])
                    break
                if case(1):
                    self.nodeStruct.i_codeCommand = int(stringData[i])
                    break
                if case(2):
                    self.nodeStruct.i_code_answer = int(stringData[i])
                    break
                if case(3):
                    self.nodeStruct.o_obj.h_idObj = int(stringData[i])
                    break
                if case(4):
                    self.nodeStruct.o_obj.h_idSubObj = int(stringData[i])
                    break
                if case(5):
                    break
                if case(6):
                    self.setValue(stringData[i])
                    # для отладки после убрать, поскольку запускаем без параметр, будет проставляться random()
                    self.setD_value()
                    break
                if case(length - 3):
                    self.nodeStruct.o_obj.i_check = int(stringData[i])
                    break
                if case():
                    break
        return i_status

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