# -*- coding: utf-8 -*-

from Server.NodeObjInfo import NodeObjInfo
from Server.AlgoritmInfo import AlgoritmInfo

class NodeInfo():
    """
    класс содержит структуру объектя для сетевого взаимодействия по протоколу CAN

    :param: * i_idNode: = 1       идентификатор узла
            * i_code_answer: = 0  код ответа от узла
            * i_codeCommand: = 0  код команды присваивается в зависимости от протокола работы узла
            * s_command: = ""     описание команды
            * s_message: = ""     строка получаемая из буфера
            * list_obj: = []      будет содержаться список NodeObjInfo
            * o_obj: = NodeObjInfo()  для nodeStruct
    """

    def __init__(self):
        self.i_idNode = 1
        self.i_code_answer = 0
        self.i_codeCommand = 0
        self.s_command = ""
        self.s_message = ""
        self.o_Algoritm=AlgoritmInfo()
        self.list_obj=[]
        self.o_obj=NodeObjInfo()
