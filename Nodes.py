# -*- coding: utf-8 -*-
import copy, random

from numpy.core import double

from switch import switch
from PLCGlobals import PLCGlobals
from MesPacked import MesPacked

class Nodes():
    errMessage= ""
    mesPacked=MesPacked()
    # коды ошибок возвращаемые методами классов, не совпадает с i_code_answer
    FIND_NODE_ERR = -1
    FIND_OBJ_ERR = -1

    def __init__(self):
        key_obj = ['h_idObj',
               'h_idSubObj',
               'i_typeData',
               'd_value',
               'i_check',
               'b_message']
        value_obj = [0x0,
                 0x0,
                 0,
                 0.0,
                 0,
                 bytes()]
        self.dict_objs = dict(zip(key_obj, value_obj))
        self.list_objs = []

        key = ['i_idNode',
               'i_code_answer',
               'i_codeCommand',
               's_command',
               's_message',
               'Objs']
        value = [0,
                 0,
                 0,
                 "",
                 "",
                 self.list_objs]
        self.dict_nodes = dict(zip(key, value))
        self.list_nodes = []

    def __del__(self):
        pass

#################################################
    def set_dict_val_obj(self, key, value):
        b_status = False
        if self.dict_objs.get(key) is not None:
            self.dict_objs[key] = value
            b_status = True
        return b_status

    def add_item_dict_obj(self, key, item):
        length=len(item)
        self.dict_objs[key]=copy.deepcopy(item)

    def add_item_objs(self, item, list_objs):
        length = len(list_objs)

        i_status = PLCGlobals.UPDATE_FAIL
        if (length == 0):
            dict_temp = item.copy()
            list_objs.append(dict_temp)
        else:
            for i in range(length):
                dict_temp = list_objs[i].copy()
                if dict_temp['h_idObj'] == item['h_idObj']:
                    list_objs[i].update(item)
                    i_status = PLCGlobals.UPDATE_OK
            if (i_status == PLCGlobals.UPDATE_FAIL):
                dict_temp = item.copy()
                list_objs.append(dict_temp)
        return list_objs

    def get_val_obj(self, id_Obj, name_field):
        result = None
        length = len(self.list_objs)
        typeVal = self.mesPacked.dict_typeData["None"]
        for i in range(length):
            if self.list_objs[i]['h_idObj'] == id_Obj:
                for case in switch(name_field):
                    if case("h_idSubObj"): pass
                    if case("i_typeData"): pass
                    if case("i_check"):
                        result = int(self.list_objs[i].get(name_field))
                        typeVal = self.mesPacked.dict_typeData["Integer"]
                        break
                    if case("d_value"):
                        result = float(self.list_objs[i].get(name_field))
                        typeVal=self.mesPacked.dict_typeData["Double"]
                        break
                    if case("b_message"):
                        result = bytes(self.list_objs[i].get(name_field))
                        typeVal=self.mesPacked.dict_typeData["Bytes"]
                        break
                    if case():
                        result = self.list_objs[i].get(name_field)
        if (result==None and typeVal==self.mesPacked.dict_typeData["None"]):
            self.messageErr="objs.get_val:".format(result,typeVal)
            self.mesPacked.print_message(self.messageErr,PLCGlobals.INFO)
            result=0
        return result

    def set_val_obj(self, list_objs, nodeStruct):
        """
        рекурсивный метод присваивает значения объектам внустри узла, в случае если
        объекта в узле не обнаружено то он рекурсивно вызывается и заносит данные
        в краткосрочный архив
        :param: list_obj: список объектов внутри узла
        :param: nodeStruct: структура содержащая идентификатор объекта внутри узла
        и все соотвествующие объекту отрибуты
        :rtype: i_status, list_objs статус и обновленный список с объектами узла
        """
        i_status = PLCGlobals.SET_VAL_FAIL
        length = len(list_objs)
        for i in range(length):
            if list_objs[i]['h_idObj'] == nodeStruct.o_obj.h_idObj:
                        list_objs[i]["h_idSubObj"] = nodeStruct.o_obj.h_idSubObj
                        list_objs[i]["i_typeData"] = nodeStruct.o_obj.i_typeData
                        list_objs[i]["d_value"] = nodeStruct.o_obj.d_value
                        length, list_objs[i]["b_message"] = \
                            self.mesPacked.setB_message(self.mesPacked.OK,
                                                        nodeStruct)
                        list_objs[i]["i_check"] = self.mesPacked.set_CRC(nodeStruct)
                        i_status = PLCGlobals.SET_VAL_OK
                        break
        if i_status == PLCGlobals.SET_VAL_FAIL:
            self.set_dict_val_obj("h_idObj", nodeStruct.o_obj.h_idObj)
            list_objs=self.add_item_objs(self.dict_objs,list_objs)
            self.set_val_obj(list_objs, nodeStruct)
        return i_status, list_objs

    def set_val_obj_old(self, list_objs, id_Obj, name_field, value=0):
        """
        метод присваивает значения объектам внустри узла
        :param: list_obj: список объектов внутри узла
        :param: id_Obj: идентификатор объекта внутри узла
        :param: name_filed: имя поля в словаре которое указывает на переменную
        :param: value: значение является необязательныйм параметром
        :rtype: object
        """
        i_status = PLCGlobals.SET_VAL_FAIL
        length = len(list_objs)
        for i in range(length):
            if list_objs[i]['h_idObj'] == id_Obj:
                for case in switch(name_field):
                    if case("h_idObj"):
                        # i_status меняет свое предназначение на индекс в списке
                        i_status = i
                        return i_status, list_objs
                    if case("h_idSubObj"):
                        list_objs[i]["h_idSubObj"] = int(value)
                        i_status = PLCGlobals.SET_VAL_OK
                        break
                    if case("i_typeData"):
                        list_objs[i]["i_typeData"] = int(value)
                        i_status = PLCGlobals.SET_VAL_OK
                        break
                    if case("d_value"):
                        list_objs[i]["d_value"] = double(value)
                        i_status = PLCGlobals.SET_VAL_OK
                        break
                    if case("b_message"):
                        length, list_objs[i]["b_message"] = \
                            self.mesPacked.setB_message(self.mesPacked.OK,
                                                        self.mesPacked.nodeStruct)
                        i_status = PLCGlobals.SET_VAL_OK
                        break
                    if case("i_check"):
                        list_objs[i]["i_check"] = self.mesPacked.set_CRC(self.mesPacked.nodeStruct)
                        i_status = PLCGlobals.SET_VAL_OK
                        break
        if i_status == PLCGlobals.SET_VAL_FAIL and "h_idObj" in name_field:
            self.set_dict_val_obj("h_idObj", value)
            list_objs=self.add_item_objs(self.dict_objs,list_objs)
        return i_status, list_objs

    def print_dict_objs(self):
        self.mesPacked.print_message(self.dict_objs,PLCGlobals.INFO)

    def print_list_obj(self):
        length = len(self.list_objs)
        for i in range(length):
            self.mesPacked.print_message(self.list_objs[i],PLCGlobals.INFO)

    def set_dict_val(self, key, value):
        b_status = False
        if self.dict_nodes.get(key) is not None:
            self.dict_nodes[key] = value
            b_status = True
        return b_status

    def add_item_dict(self, key, item):
        length=len(item)
        self.dict_nodes[key]=copy.deepcopy(item)

    def add_item_nodes(self, item):
        length = len(self.list_nodes)
        self.add_item_dict('Objs',[])

        i_status = PLCGlobals.UPDATE_FAIL
        if (length == 0):
            dict_temp = item.copy()
            self.list_nodes.append(dict_temp)
            i_status = PLCGlobals.ADD_OK
        else:
            for i in range(length):
                dict_temp = self.list_nodes[i].copy()
                if dict_temp['i_idNode'] == item['i_idNode']:
                    self.list_nodes[i].update(item)
                    i_status = PLCGlobals.UPDATE_OK
            if (i_status == PLCGlobals.UPDATE_FAIL):
                dict_temp = item.copy()
                self.list_nodes.append(dict_temp)
                i_status=PLCGlobals.ADD_OK
        return i_status

    def get_val(self, id_Node, name_field):
        result = None
        length = len(self.list_nodes)
        typeVal = self.mesPacked.dict_typeData["None"]
        for i in range(length):
            if self.list_nodes[i]['i_idNode'] == id_Node:
                for case in switch(name_field):
                    if case("i_code_answer"): pass
                    if case("i_codeCommand"):
                        result = int(self.list_nodes[i].get(name_field))
                        typeVal = self.mesPacked.dict_typeData["Integer"]
                        break
                    if case("s_command"): pass
                    if case("s_message"):
                        result = self.list_nodes[i].get(name_field)
                        typeVal = self.mesPacked.dict_typeData["String"]
                        break
                    if case("Objs"):
                        result = self.list_nodes[i].get(name_field)
                        typeVal=self.mesPacked.dict_typeData["Object"]
                        break
                    if case():
                        result = self.list_nodes[i].get(name_field)
                        break
        if (result==None and typeVal==self.mesPacked.dict_typeData["None"]):
            self.messageErr="nodes.get_val:".format(result,typeVal)
            self.mesPacked.print_message(self.messageErr,PLCGlobals.INFO)
            result=0
        return result

    def set_val(self, id_Node, name_field, value=0):
        i_status = PLCGlobals.SET_VAL_FAIL
        length = len(self.list_nodes)
        i_index=length-1
        for i in range(length):
            if self.list_nodes[i]['i_idNode'] == id_Node:
                i_index=i
                for case in switch(name_field):
                    if case("i_code_answer"):
                        self.list_nodes[i]["i_code_answer"] = int(value)
                        i_status = PLCGlobals.SET_VAL_OK
                        break
                    if case("i_codeCommand"):
                        self.list_nodes[i]["i_codeCommand"] = int(value)
                        i_status = PLCGlobals.SET_VAL_OK
                        break
                    if case("s_command"):
                        self.list_nodes[i]["s_command"] = str(value)
                        i_status = PLCGlobals.SET_VAL_OK
                        break
                    if case("s_message"):
                        self.list_nodes[i]["s_message"] = str(value)
                        i_status = PLCGlobals.SET_VAL_OK
                        break
                    if case("Objs"):
                        self.list_nodes[i]["Objs"]=value
                        i_status = PLCGlobals.SET_VAL_OK
                        break
                    if case():
                        result = self.list_nodes[i].get(name_field)
                        i_status = PLCGlobals.UPDATE_OK
                        break
        if i_status == PLCGlobals.SET_VAL_FAIL and "i_idNode" in name_field:
            self.set_dict_val("i_idNode", value)
            i_status=self.add_item_nodes(self.dict_nodes)
        return i_status, i_index

    def find_node(self, id_node):
        length = len(self.list_nodes)
        for i in range(length):
            if self.list_nodes[i]["i_idNode"]==id_node:
                return i, self.list_nodes[i]["Objs"]
        return self.FIND_NODE_ERR, None

    def find_obj(self, id_obj, objs):
        length = len(objs)
        for i in range(length):
            if objs[i]["h_idObj"]==id_obj:
                return i
        return self.FIND_OBJ_ERR

    def find_node_obj(self, id_node, id_obj):
        """
        метод ищет в хранилище данных данные по идентификатору узла и объекта
        возвращает индекс узла в списке узлов, а также индекс найденной объекта
        в списке объектов
        :param id_node:
        :param id_obj:
        :return: i, i_obj:  индекс узла, индек объекта
        """
        i, objs = self.find_node(id_node)
        if i!=self.FIND_NODE_ERR:
            i_obj=self.find_obj(id_obj,objs)
            return  i, i_obj
        else:
            return i, self.FIND_NODE_ERR


    def print_dict_nodes(self):
        self.mesPacked.print_message(self.dict_nodes,PLCGlobals.INFO)

    def print_list_nodes(self):
        length = len(self.list_nodes)
        for i in range(length):
            str_node_info="i_idNode:{0:d};i_code_answer:{1:d}({1:X});" \
                          "i_codeCommand:{2:d}({2:X});" \
                          "s_commans:{3:<20s};" \
                          "s_message:{4:<20s}".format(
                self.list_nodes[i]['i_idNode'],
                self.list_nodes[i]["i_code_answer"],
                self.list_nodes[i]["i_codeCommand"],
                self.list_nodes[i]["s_command"],
                self.list_nodes[i]["s_message"])
            self.mesPacked.print_message(str_node_info,PLCGlobals.INFO)
            len_objs=len(self.list_nodes[i]["Objs"])
            self.messageErr="Objs length:{0:3d} objs".format(len_objs)
            self.mesPacked.print_message(self.messageErr,PLCGlobals.INFO)
            for j in range(len_objs):
                str_node_info="h_idObj:{0:d}({0:X});" \
                    "h_idSubObj:{1:d}({1:X});" \
                    "d_value:{2:4.6f};" \
                    "i_typeData:{3:d};" \
                    "b_message:{4:<10s}".format(
                    self.list_nodes[i]["Objs"][j]['h_idObj'],
                    self.list_nodes[i]["Objs"][j]['h_idSubObj'],
                    self.list_nodes[i]["Objs"][j]['d_value'],
                    self.list_nodes[i]["Objs"][j]['i_typeData'],
                    self.list_nodes[i]["Objs"][j]['b_message']
                )
                self.mesPacked.print_message(str_node_info,PLCGlobals.INFO)

################################ start section #################################
def loadObjs(index_node,nodes):
    # тестируем объекты в узлах
    for i in range(1, 10):
        i_idNode=nodes.list_nodes[index_node]['i_idNode']
        h_idObj=0x1000+random.randint(1,10)
        h_idSubObj=0x0+i
        d_value=random.random()
        nodeStruct=nodes.mesPacked.initNodeStruct(i_idNode,h_idObj,h_idSubObj,d_value)
        nodes.set_val_obj(nodes.list_nodes[index_node]['Objs'],nodeStruct)

    return nodes.list_nodes[index_node]['Objs']

if __name__ == '__main__':
    global debug

    errMessage = "py_runtime start..."

    nodes = Nodes()

    # тестируем узлы
    for i in range(1, 10):
        id_Node=random.randint(1,10)
        i_status, i_index=nodes.set_val(id_Node,"i_idNode",id_Node)
        nodes.set_val(id_Node,"i_code_answer",nodes.mesPacked.OK)
        nodes.set_val(id_Node,"i_codeCommand",nodes.mesPacked.CODE_START)
        nodes.set_val(id_Node,"s_command",nodes.mesPacked.dict_classif[nodes.mesPacked.CODE_START])
        nodes.set_val(id_Node,"s_message",nodes.mesPacked.dict_classif[nodes.mesPacked.OK])
        nodes.set_val(id_Node,"Objs",loadObjs(i_index,nodes))

    id_node=7
    id_nodeObj=0x1000+5

    i, i_obj=nodes.find_node_obj(id_node,id_nodeObj)
    if (i!=nodes.FIND_NODE_ERR and
        i_obj!=nodes.FIND_OBJ_ERR):
        str_node_info = "i_idNode:{0:d};" \
                        "i_code_answer:{1:d}({1:X});" \
                        "i_codeCommand:{2:d}({2:X});" \
                        "s_command:{3:<20s};" \
                        "s_message:{4:<10s}\n"\
                        "\th_idObj:{5:d}({5:X});" \
                        "h_idSubObj:{6:d}({6:X});" \
                        "i_typeData:{7:d};" \
                        "i_check:{8:d};" \
                        "b_message:{9:s}" \
            .format(
            nodes.list_nodes[i]['i_idNode'],
            nodes.list_nodes[i]["i_code_answer"],
            nodes.list_nodes[i]["i_codeCommand"],
            nodes.list_nodes[i]["s_command"],
            nodes.list_nodes[i]["s_message"],
            nodes.list_nodes[i]['Objs'][i_obj]['h_idObj'],
            nodes.list_nodes[i]['Objs'][i_obj]['h_idSubObj'],
            nodes.list_nodes[i]['Objs'][i_obj]['i_typeData'],
            nodes.list_nodes[i]['Objs'][i_obj]['i_check'],
            nodes.list_nodes[i]['Objs'][i_obj]['b_message']
        )
        nodes.mesPacked.print_message(str_node_info, PLCGlobals.INFO)

    nodes.print_list_nodes()

