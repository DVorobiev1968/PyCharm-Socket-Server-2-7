# -*- coding: utf-8 -*-

from NodeObjInfo import NodeObjInfo

class NodeInfo():
    """
    :param: i_idNode = 1       идентификатор узла
    :param: i_code_answer = 0  код ответа от узла
    :param: i_codeCommand = 0  код команды присваивается в зависимости от протокола работы узла
    :param: s_command = ""     описание команды
    :param: s_message = ""     строка получаемая из буфера
    :param: list_obj = []      будет содержаться список NodeObjInfo
    :param: o_obj = NodeObjInfo()  для nodeStruct
    """

    def __init__(self):
        self.i_idNode = 1
        self.i_code_answer = 0
        self.i_codeCommand = 0
        self.s_command = ""
        self.s_message = ""
        self.list_obj=[]
        self.o_obj=NodeObjInfo()
