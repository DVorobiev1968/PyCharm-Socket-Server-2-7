# -*- coding: utf-8 -*-

class NodeObjInfo():
    """
    класс содержит описание структуры объекта узла, для организации краткосрочного архива,
    межсетевого взаимодействия.

    :param: * h_idObj: = 0x1:        идентификатор объекта
            * h_idSubObj: = 0x100:   идентификатор субобъекта
            * i_typeData: = 0        тип данных объекта
            * d_value: = 0.1         возвращаемое значение
            * i_check: = 0           контрольная сумма
            * b_message: = bytes()   массив байт принимаемый от клиента
            * s_message: = str()     строка с учетом кодировки отправляемая клиенту
            * b_obj:=bytes()         дополнительный объект для сериализации

    """

    def __init__(self):
        self.h_idObj = 0x1
        self.h_idSubObj = 0x100
        self.i_typeData = 0
        self.d_value = 0.1
        self.i_check = 0
        self.b_message = bytes()
        self.s_message = str()
        self.b_obj=bytes()
