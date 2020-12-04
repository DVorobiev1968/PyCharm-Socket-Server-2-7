# -*- coding: utf-8 -*-

class NodeObjInfo():
    def __init__(self):
        """
        :param: h_idObj = 0x1:        идентификатор объекта
        :param: h_idSubObj = 0x100:   идентификатор субобъекта
        :param: i_typeData = 0        тип данных объекта
        :param: d_value = 0.1         возвращаемое значение
        :param: i_check = 0           контрольная сумма
        :param: b_message = bytes()   массив байт отправляемый клиенту
        :param: b_obj=bytes()         дополнительный объект для сериализации
        """
        self.h_idObj = 0x1
        self.h_idSubObj = 0x100
        self.i_typeData = 0
        self.d_value = 0.1
        self.i_check = 0
        self.b_message = bytes()
        self.b_obj=bytes()
