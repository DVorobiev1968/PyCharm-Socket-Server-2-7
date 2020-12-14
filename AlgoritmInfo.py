# -*- coding: utf-8 -*-
import datetime

class AlgoritmInfo():
    def __init__(self):
        """
        :param: status          статус берется из Classif, отражает состояние расчета алгоритма ФБ-ом
        :param: dateTime        метка времени рассчета алгоритма ФБ-ом
        """
        self.status = 0
        self.dateTime = datetime.datetime.now()
