# -*- coding: utf-8 -*-
import datetime

class AlgoritmInfo():
    def __init__(self,status=50):
        """
        По умолчанию устнавливаем статуи в CODE_ALGORITM_OPERATION
        :@type status: int          статус берется из Classif, отражает состояние расчета алгоритма ФБ-ом
        """
        self.status = status
        self.dateTime = datetime.datetime.now()
    def __repr__(self):
        return "{0};{1}".format(self.status,self.dateTime.strftime("%d.%m.%Y %H:%M:%S.%f"))
    def __str__(self):
        return "{0}->{1}".format(self.status,self.dateTime.strftime("%d.%m.%Y %H:%M:%S.%f"))
    def __hash__(self):
        return hash(self.status)
    def __len__(self):
        """
        переопределяем метод, выставляем что кол-во элементов 2
        :rtype: object
        """
        return 2