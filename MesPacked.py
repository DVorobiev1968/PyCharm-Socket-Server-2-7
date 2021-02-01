# -*- coding: utf-8 -*-

import re, random, sys, pickle, copy

if sys.version_info < (3, 7):
    if sys.platform == "linux" or sys.platform == "linux2":
        def double(arg):
            return float(arg)
    elif sys.platform == "darwin":
        pass
    elif sys.platform == "win32":
        from numpy.core import double
else:
    if sys.platform == "linux" or sys.platform == "linux2":
        def double(arg):
            return float(arg)
    elif sys.platform == "darwin":
        pass
    elif sys.platform == "win32":
        from decimal import Decimal
        def double(arg):
            return Decimal(arg)

from switch import switch
from PLCGlobals import PLCGlobals
from NodeInfo import NodeInfo
from AlgoritmInfo import AlgoritmInfo


class MesPacked():
    """
    Класс для определения структур в соотвествии с протоколом CAN, для сетевого взаимодействия
    Обеспечение сетевого вхаимодействия между сервером и клиентом

    Коды блока готовности Алгоритмов и их описание:
        * CODE_ALGORITM_OPERATION = 50
        * SET_ALGORITM_VAL_OK = CODE_ALGORITM_OPERATION + PLCGlobals.SET_VAL_OK
        * SET_ALGORITM_VAL_FAIL = CODE_ALGORITM_OPERATION + PLCGlobals.SET_VAL_FAIL
        * SET_ALGORITM_WAIT = CODE_ALGORITM_OPERATION + PLCGlobals.UPDATE_FAIL

    Коды i_code_answer и их описание:
        * CODE_NODES_OPERATION = 60
        * ADD_OK = CODE_NODES_OPERATION + PLCGlobals.ADD_OK
        * ADD_FAIL = CODE_NODES_OPERATION + PLCGlobals.ADD_FAIL
        * UPDATE_OK = CODE_NODES_OPERATION + PLCGlobals.UPDATE_OK
        * UPDATE_FAIL = CODE_NODES_OPERATION + PLCGlobals.UPDATE_FAIL
        * SET_VAL_OK = CODE_NODES_OPERATION + PLCGlobals.SET_VAL_OK
        * SET_VAL_FAIL = CODE_NODES_OPERATION + PLCGlobals.SET_VAL_FAIL
        * SEARCH_FAIL = 78
        * SEARCH_OK = 79
        * OK = 80
        * ERR = 99
        * SYNTAX_ERR = 101

    Коды команд Сервера технологических данных:
        #. CODE_START = 1: Множественная загрузка узлов с инициализацией значений тэгов в каждом
        #. CODE_STOP = 2: Останов Сервера внутри сессии
        #. CODE_SINGLE_START = 3: Команда на одиночную работу с конкретным узлом
        #. CODE_SINGLE_START_SYNC = 4: Команда на одиночную работу с конкретным узлом в режиме синхронной передачи данных
        #. CODE_SINGLE_START_ASYNC = 5: Команда на одиночную работу с конкретным узлом в режиме асинхронной передачи данных
        #. CODE_LIST_NODES = 10: Команда на формирования перечня загруженных узлов в краткосрочном архиве
        #. CODE_FIND_NODES = 11: Команда на поиск созданного узла
        #. CODE_FIND_NODES_SYNC = 12: Команда на поиск созданного узла в режиме синхронной передачи данных
        #. CODE_LOAD_FOR_ALGORITM = 13: Команда на загрузку данных для использования в ФБ Beremiz.
        #. CODE_SAVE_FOR_ALGORITM = 14: Команда на запись данных в алгоритме реализованном в ФБ Beremiz
        #. CODE_EXIT = 20: Команда завершения текущей сессии работы клиента
        #. CODE_EXIT_SERVER = 21: Команда завершения работы Сервера технологических данных

    Cетевые настройки:
        * port = 8889

    Описание классификатора:
        * ``OK``: "Command completed completely"
        * ``CODE_START``: "Start command"
        * ``CODE_STOP``: "Stop command"
        * ``CODE_SINGLE_START``: "Single start command"
        * ``CODE_SINGLE_START_SYNC``: "Single start command synchronisation with FB"
        * ``CODE_SINGLE_START_ASYNC``: "Single start command no wait synchronisation with FB"
        * ``CODE_LIST_NODES``: "Printing nodes list"
        * ``CODE_FIND_NODES``: "Search nodes and objext"
        * ``CODE_FIND_NODES_SYNC``: "Search nodes and objext synchronisation with FB"
        * ``CODE_LOAD_FOR_ALGORITM``: "Search nodes and objext and load data of node for Algoritm"
        * ``CODE_SAVE_FOR_ALGORITM``: "Save data from Algoritm"
        * ``CODE_EXIT``: "Close connect Client stopped"
        * ``CODE_EXIT_SERVER``: "Close connect Server stopped"
        * ``CODE_NODES_OPERATION``: "Codes Error/Info for node and object"
        * ``SEARCH_OK``: "Node and object found OK"
        * ``SEARCH_FAIL``: "Node and object not found"
        * ``ADD_OK``: "Add list_node/list_obj it`s OK"
        * ``ADD_FAIL``: "Add list_node/list_obj it`s FAIL"
        * ``UPDATE_OK``: "Update list_node/list_obj  it`s OK"
        * ``UPDATE_FAIL``: "Update list_node/list_obj it`s FAIL"
        * ``SET_VAL_OK``: "Set list_node/list_obj it`s OK"
        * ``SET_VAL_FAIL``: "Set list_node/list_obj it`s FAIL"
        * ``CODE_ALGORITM_OPERATION``: "Codes Error/Info for Algoritm"
        * ``SET_ALGORITM_VAL_OK``: "Algoritm calculate completed"
        * ``SET_ALGORITM_VAL_FAIL``: "Algoritm calculate it`s fail"
        * ``SET_ALGORITM_WAIT``: "Wait for Algoritm calculated..."
        * ``ERR``: "General error"

    """

    def __init__(self):
        """
        Инициализация класса для реализации протокола CAN
        """

        self.code_status = 0
        self.errMessage = str("")
        self.DELIM = str(";\r\n")
        self.LEN_DELIM = 3
        # коды блока готовности Алгоритмов и их описание
        self.CODE_ALGORITM_OPERATION = 50
        self.SET_ALGORITM_VAL_OK = self.CODE_ALGORITM_OPERATION + PLCGlobals.SET_VAL_OK
        self.SET_ALGORITM_VAL_FAIL = self.CODE_ALGORITM_OPERATION + PLCGlobals.SET_VAL_FAIL
        self.SET_ALGORITM_WAIT = self.CODE_ALGORITM_OPERATION + PLCGlobals.UPDATE_FAIL

        # коды i_code_answer и их описание
        self.CODE_NODES_OPERATION = 60
        self.ADD_OK = self.CODE_NODES_OPERATION + PLCGlobals.ADD_OK
        self.ADD_FAIL = self.CODE_NODES_OPERATION + PLCGlobals.ADD_FAIL
        self.UPDATE_OK = self.CODE_NODES_OPERATION + PLCGlobals.UPDATE_OK
        self.UPDATE_FAIL = self.CODE_NODES_OPERATION + PLCGlobals.UPDATE_FAIL
        self.SET_VAL_OK = self.CODE_NODES_OPERATION + PLCGlobals.SET_VAL_OK
        self.SET_VAL_FAIL = self.CODE_NODES_OPERATION + PLCGlobals.SET_VAL_FAIL
        self.SEARCH_FAIL = 78
        self.SEARCH_OK = 79
        self.OK = 80
        self.ERR = 99
        self.SYNTAX_ERR = 101

        # коды команд
        self.CODE_START = 1
        self.CODE_STOP = 2
        self.CODE_SINGLE_START = 3
        self.CODE_SINGLE_START_SYNC = 4
        self.CODE_SINGLE_START_ASYNC = 5
        self.CODE_LIST_NODES = 10
        self.CODE_FIND_NODES = 11
        self.CODE_FIND_NODES_SYNC = 12
        self.CODE_LOAD_FOR_ALGORITM = 13
        self.CODE_SAVE_FOR_ALGORITM = 14
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
            "Object": 7,
            "Algoritm": 8
        }
        self.dict_classif = {
            self.OK: "Command completed completely",
            self.CODE_START: "Start command",
            self.CODE_STOP: "Stop command",
            self.CODE_SINGLE_START: "Single start command",
            self.CODE_SINGLE_START_SYNC: "Single start command synchronisation with FB",
            self.CODE_SINGLE_START_ASYNC: "Single start command no wait synchronisation with FB",
            self.CODE_LIST_NODES: "Printing nodes list",
            self.CODE_FIND_NODES: "Search nodes and objext",
            self.CODE_FIND_NODES_SYNC: "Search nodes and objext synchronisation with FB",
            self.CODE_LOAD_FOR_ALGORITM: "Search nodes and objext and load data of node for Algoritm",
            self.CODE_SAVE_FOR_ALGORITM: "Save data from Algoritm",
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
            self.SET_VAL_FAIL: "Set list_node/list_obj it`s FAIL",
            self.CODE_ALGORITM_OPERATION: "Codes Error/Info for Algoritm",
            self.SET_ALGORITM_VAL_OK: "Algoritm calculate completed",
            self.SET_ALGORITM_VAL_FAIL: "Algoritm calculate it`s fail",
            self.SET_ALGORITM_WAIT: "Wait for Algoritm calculated...",
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

        self.nodeStruct = NodeInfo()  # переменная узел

    def print_message(self, messageErr, key):
        """
        Вывод диагностических сообщений по работе приложения

        :param: * messageErr: текст сообщения
                * key: код для фильтрации сообщений

        """
        key_head=key-PLCGlobals.NO_HEAD
        head=True
        if key_head > 0:
            head=False
            key=key_head
        if PLCGlobals.debug <= key:
            if head:
                s_print = "{0:1d}:{1:<40s}".format(key, messageErr)
            else:
                s_print = "{1:<40s}".format(key, messageErr)
            print(s_print)
            sys.stdout.flush()

    def initNodeStruct(self, id_node, idObj, idSubObj, d_value):
        """
        метод для отладки инициализирует переменную
        содержащую структуру узла, с описанием объектов
        внутри применяется только для отладки, в рабочем режиме
        nodeStruct заполняется при получении данных от клиента

        :param: * id_node: номер узла
                * idObj: номер объекта
                * idSubObj: номер субобъекта
                * d_value: значение для инициализации переменной (тэга) узла

        :return: nodeStruct: объект типа nodeStruct

        """
        nodeStruct = NodeInfo()  # переменная узел
        nodeStruct.i_idNode = id_node
        # код команды присваивается в зависимости от протокола работы узла
        nodeStruct.i_codeCommand = self.CODE_START
        # описание команды
        nodeStruct.s_command = self.dict_classif[self.nodeStruct.i_codeCommand]
        # строка получаемая из буфера
        nodeStruct.s_message = self.dict_classif[self.nodeStruct.i_codeCommand]
        nodeStruct.o_obj.__init__()
        nodeStruct.o_obj.h_idObj = 0x0 + idObj
        nodeStruct.o_obj.h_idSubObj = 0x0 + idSubObj
        nodeStruct.o_obj.i_typeData = self.dict_typeData["Double"]
        nodeStruct.o_obj.d_value = d_value
        nodeStruct.o_Algoritm.__init__(self)
        nodeStruct.o_Algoritm.status = self.SET_ALGORITM_VAL_FAIL
        return copy.deepcopy(nodeStruct)

    def setAlgoritmStruct(self, i_command, i_code_answer=0):
        """
         метод инициализирует переменную
         содержащую структуру Алгоритма

         :param: * i_command: код команды
                * i_code_answer: код ответа на команду (статуc), параметр опциональный

         :return: algoritmInfo: объект типа AlgoritmInfo

         """
        algoritmInfo = AlgoritmInfo(i_command)
        if i_command == self.CODE_LOAD_FOR_ALGORITM:
            algoritmInfo.status = self.SET_ALGORITM_WAIT
        elif i_command == self.CODE_SAVE_FOR_ALGORITM:
            algoritmInfo.status = self.SET_ALGORITM_VAL_OK
        else:
            algoritmInfo.status = self.SET_ALGORITM_VAL_FAIL
        return algoritmInfo

    def setCommandNodeStruct(self, i_command, i_code_answer=0, id_node=0, idObj=0, idSubObj=0, d_value=0):
        """
        метод для отладки инициализирует переменную
        содержащую структуру узла, с описанием объектов
        внутри применяется только для отладки, в рабочем режиме
        nodeStruct заполняется при получении данных от клиента

        :param: * i_command: код команды
                * i_code_answer: код ответа на команду (статут)
                * id_node: идентификатор узла
                * idObj: идентификатор объекта
                * idSubObj: идентификатор субобъекта
                * d_value: значение

        :return: nodeStruct: объект типа nodeStruct

        """
        nodeStruct = NodeInfo()  # переменная узел
        nodeStruct.i_idNode = id_node
        # код команды присваивается в зависимости от протокола работы узла
        nodeStruct.i_codeCommand = i_command
        # описание команды
        nodeStruct.s_command = self.dict_classif[self.nodeStruct.i_codeCommand]
        # строка получаемая из буфера
        nodeStruct.s_message = self.dict_classif[self.nodeStruct.i_codeCommand]
        # статус ответа OK
        if (i_code_answer == 0):
            nodeStruct.i_code_answer = self.OK
        else:
            nodeStruct.i_code_answer = i_code_answer

        nodeStruct.o_obj.h_idObj = 0x0 + idObj
        nodeStruct.o_obj.h_idSubObj = 0x0 + idSubObj
        nodeStruct.o_obj.i_typeData = self.dict_typeData["Double"]
        nodeStruct.o_obj.d_value = d_value
        nodeStruct.o_Algoritm = self.setAlgoritmStruct(i_command)
        return nodeStruct

    def setB_message(self, code_err=0, nodeStruct=NodeInfo()):
        """
        метод подготовливает 2 строки для сериализации:
            #. b_message- упрощеная строка содержит информмацию из строкового представления
            #. b_obj - расширенная непосредственно объект для сериализауии

        :param: * code_err: код ответа узла
                * nodeStruct: объект со структурой узла

        :return: * i_length: длина
                * nodeStruct: структура сообщения

        """
        i_length = 0
        if code_err == 0:
            code_err = nodeStruct.i_code_answer

        s_message = "{0};{1};{2};{3};{4};{5};{6}".format(
            nodeStruct.i_idNode,
            nodeStruct.i_codeCommand,
            code_err,
            nodeStruct.o_obj.h_idObj,
            nodeStruct.o_obj.h_idSubObj,
            nodeStruct.o_obj.i_typeData,
            nodeStruct.o_obj.d_value)
        i_length = len(s_message)
        i_length += len(str(i_length))
        i_length += self.LEN_DELIM
        nodeStruct.o_obj.s_message = "{0};{1}{2}".format(s_message, i_length, self.DELIM)
        if sys.version_info < (3, 7):
            nodeStruct.o_obj.b_message = bytes(nodeStruct.o_obj.s_message)
        else:
            nodeStruct.o_obj.b_message = bytes(nodeStruct.o_obj.s_message, 'utf-8')
        # nodeStruct.o_obj.s_message=str(nodeStruct.o_obj.b_message,'utf-8')
        nodeStruct.o_obj.b_obj = pickle.dumps(nodeStruct, 0)
        i_length_obj = len(nodeStruct.o_obj.b_obj)
        return i_length, nodeStruct

    def set_CRC(self, nodeStruct):
        """
        метод расчитывает котрольную сумму по b_message

        :param: nodeStruct: структура сообщения

        :return: i_crc: в качестве контрольной суммы кол-во символов (байт) в телеграмме

        """
        i_crc = len(nodeStruct.o_obj.b_message)
        return i_crc

    def set_CRC_b_obj(self, nodeStruct):
        """
        метод расчитывает котрольную сумму по b_obj

        :param: nodeStruct: структура сообщения

        :return: i_crc: в качестве контрольной суммы кол-во символов (байт) в телеграмме

        """
        i_crc = len(nodeStruct.o_obj.b_obj)
        return i_crc

    def sendMessage(self, i_data, nodeStruct):
        """
        Читаем св-ва класса и дополняем кодом ответа

        :param: * i_data: кол-во символов в телеграмме
                * nodeStruct: структура сообщения

        :return: * i_status: код ошибки
                * i_length: длина телеграммы
                * nodeStruct: структура как объект

        """
        i_status = self.OK
        i_length = 0
        b_message = bytes()
        b_obj = bytes()
        if i_data >= nodeStruct.o_obj.i_check:
            if nodeStruct.i_codeCommand == self.CODE_START:
                i_length, nodeStruct = self.setB_message(self.OK, nodeStruct)
                i_status = self.OK
            elif nodeStruct.i_codeCommand == self.CODE_SINGLE_START:
                i_length, nodeStruct = self.setB_message(self.OK, nodeStruct)
                i_status = self.OK
            elif nodeStruct.i_codeCommand == self.CODE_STOP:
                i_length, nodeStruct = self.setB_message(self.OK, nodeStruct)
                i_status = self.OK
        else:
            i_length, nodeStruct = self.setB_message(self.ERR, nodeStruct)
            i_status = self.ERR

        return i_status, i_length, nodeStruct

    def recvMessage(self, data, nodeStruct):
        """
        Метод принимает строку байт от клиента и проверяет на целостность данных

        :param: * data: байтовая строка
                * nodeStruct: объект nodeStruct

        :return: * i_status: код ошибки
                * NodeInfo(): обработанный объект nodeStruct

        """
        if len(data) > 1:
            i_status = self.OK
            parse_str = re.split("[b';\r\n\s]", data)
            i_data = len(data)
            nodeStruct = self.readData(parse_str, nodeStruct)
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

        :param: data: байтовая строка

        :return: * i_status: код ошибки
                * NodeInfo(): обработанный объект nodeStruct

        """
        if len(data) > 1:
            i_status = self.OK
            parse_str = re.split("[b';\r\n]", data)
            i_data = len(data)
            nodeStruct = self.readDataNodeStruct(parse_str)
            self.errMessage = "{0}:{1:d}:{2}".format(object.__name__,
                                                     nodeStruct.o_obj.i_check,
                                                     parse_str)
            self.print_message(self.errMessage, PLCGlobals.INFO)
            i_status, \
            i_length, \
            self.nodeStruct = self.sendMessage(i_data, nodeStruct)

            return i_status, nodeStruct
        else:
            return self.SEARCH_FAIL, NodeInfo()

    def setValue(self, strValue, nodeStruct):
        """
        Метод проверяет тип данных значения и устанавливает соответствующий тип данных

        :param: strValue: строка для парсера

        :return: nodeStruct: заполненная структура узла

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

        :param: strValue: строка для парсера

        :return: * i_typeData: тип данных описание см. в классификаторе
                * d_value: значение тэга узла

        """
        i_typeData = 0
        d_value = 0
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

        :param: * nodeStruct: структура узла
                * d_value: значение которое записывается в тэг узла

        :return: nodeStruct: заполненная структура узла

        """
        if d_value == 0:
            nodeStruct.o_obj.d_value *= random.random()
        else:
            nodeStruct.o_obj.d_value = d_value
        return nodeStruct

    def readData(self, stringData, nodeStruct):
        """
        Метод парсит телеграмму от клиента раскладывает ее в поля

        :param: * stringData: в соответствии с принятым соглашением по телеграмме
                * nodeStruct: структура узла

        :return * i_status: код ошибки, заполненная структура узла
                * nodeStruct: заполненная структура узла

        """
        length = len(stringData)
        index = 0
        for i in range(length):
            if len(stringData[i]) > 0:
                for case in switch(index):
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
                        nodeStruct = self.setValue(stringData[i], nodeStruct)
                        # для отладки после убрать, поскольку запускаем без параметр, будет проставляться random()
                        # nodeStruct=self.setD_value(nodeStruct)
                        break
                    if case(7):
                        nodeStruct.o_obj.i_check = int(stringData[i])
                        break
                    if case():
                        break
                index += 1
        return nodeStruct

    def readDataNodeStruct(self, stringData):
        """
        Метод парсит телеграмму от клиента раскладывает ее в поля
        данные записываются в переменную nodeStruct, содержащую строктуру узла и объекта

        :param: stringData: в соответствии с принятым соглашением по телеграмме

        :return: nodeStruct: заполненная структура узла

        """
        i_status = self.OK
        length = len(stringData)
        nodeStruct = NodeInfo()
        index = 0
        for i in range(length):
            if len(stringData[i]) > 0:
                for case in switch(index):
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
                        #nodeStruct.o_obj.i_typeData = int(stringData[i])
                        break
                    if case(6):
                        nodeStruct.o_obj.i_typeData, \
                        nodeStruct.o_obj.d_value = self.setValueNodeStruct(stringData[i])
                        break
                    if case(7):
                        nodeStruct.o_obj.i_check = int(stringData[i])
                        break
                    if case():
                        break
                index += 1
        return nodeStruct
