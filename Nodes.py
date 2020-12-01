# -*- coding: utf-8 -*-
import copy, random
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

    def add_item_objs(self, item):
        length = len(self.list_objs)

        i_status = PLCGlobals.UPDATE_FAIL
        if (length == 0):
            dict_temp = item.copy()
            self.list_objs.append(dict_temp)
        else:
            for i in range(length):
                dict_temp = self.list_objs[i].copy()
                if dict_temp['h_idObj'] == item['h_idObj']:
                    self.list_objs[i].update(item)
                    i_status = PLCGlobals.UPDATE_OK
            if (i_status == PLCGlobals.UPDATE_FAIL):
                dict_temp = item.copy()
                self.list_objs.append(dict_temp)

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
                        typeVal=self.mesPacked.dict_typeData["Float"]
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

    def set_val_obj(self, id_Obj, name_field, value=0):
        i_status = PLCGlobals.SET_VAL_FAIL
        length = len(self.list_objs)
        for i in range(length):
            if self.list_objs[i]['h_idObj'] == id_Obj:
                for case in switch(name_field):
                    if case("h_idSubObj"):
                        self.list_objs[i]["h_idSubObj"] = int(value)
                        i_status = PLCGlobals.SET_VAL_OK
                        break
                    if case("i_typeData"):
                        self.list_objs[i]["i_typeData"] = int(value)
                        i_status = PLCGlobals.SET_VAL_OK
                        break
                    if case("d_value"):
                        self.list_objs[i]["d_value"] = float(value)
                        i_status = PLCGlobals.SET_VAL_OK
                        break
                    if case("b_message"):
                        length, self.list_objs[i]["b_message"] = \
                            self.mesPacked.setB_message(self.mesPacked.OK,
                                                        self.mesPacked.nodeStruct)
                        i_status = PLCGlobals.SET_VAL_OK
                        break
                    if case("i_check"):
                        self.list_objs[i]["i_check"] = self.mesPacked.set_CRC(self.mesPacked.nodeStruct)
                        i_status = PLCGlobals.SET_VAL_OK
                        break
        if i_status == PLCGlobals.SET_VAL_FAIL and "h_idObj" in name_field:
            self.set_dict_val_obj("h_idObj", value)
            self.add_item_objs(self.dict_objs)
        return i_status

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
        if (result==None and typeVal==self.mesPacked.dict_typeData["None"]):
            self.messageErr="nodes.get_val:".format(result,typeVal)
            self.mesPacked.print_message(self.messageErr,PLCGlobals.INFO)
            result=0
        return result

    def set_val(self, id_Node, name_field, value=0):
        i_status = PLCGlobals.SET_VAL_FAIL
        length = len(self.list_nodes)
        for i in range(length):
            if self.list_nodes[i]['i_idNode'] == id_Node:
                for case in switch(name_field):
                    if case("i_code_answer"):
                        self.list_nodes[i]["i_code_answer"] = str(value)
                        i_status = PLCGlobals.SET_VAL_OK
                        break
                    if case("i_codeCommand"):
                        self.list_nodes[i]["i_codeCommand"] = str(value)
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
        if i_status == PLCGlobals.SET_VAL_FAIL and "i_idNode" in name_field:
            self.set_dict_val("i_idNode", value)
            i_status=self.add_item_nodes(self.dict_nodes)
        return i_status

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
            self.mesPacked.print_message(self.list_nodes[i],PLCGlobals.INFO)
            len_objs=len(self.list_nodes[i]["Objs"])
            self.messageErr="Objs:{0:3d}".format(len_objs)
            self.mesPacked.print_message(self.messageErr,PLCGlobals.INFO)
            for j in range(len_objs):
                 self.mesPacked.print_message(self.list_nodes[i]["Objs"][j], PLCGlobals.INFO)

################################ start section #################################
def loadObjs(id_node,nodes):
    # тестируем объекты в узлах
    for i in range(1, 10):
        h_idObj=0x1000+i
        h_idSubObj=0x0
        d_value=random.random()
        nodes.set_val_obj(h_idObj,"h_idObj",h_idObj)
        nodes.set_val_obj(h_idObj,"h_idSubObj",h_idSubObj)
        nodes.set_val_obj(h_idObj,"i_typeData",nodes.mesPacked.dict_typeData["Float"])
        nodes.set_val_obj(h_idObj,"d_value",d_value)
        # objs.mesPacked.initNodeStruct(id_node,h_idObj,h_idSubObj,d_value)
        # objs.set_val(h_idObj, "b_message")
        # objs.set_val(h_idObj, "i_check")
    return nodes.list_objs
if __name__ == '__main__':
    global debug

    errMessage = "py_runtime start..."

    nodes = Nodes()

    # тестируем узлы
    for i in range(1, 10):
        i_status=nodes.set_val(i,"i_idNode",i)
        nodes.set_val(i,"i_code_answer",nodes.mesPacked.OK)
        nodes.set_val(i,"i_codeCommand",nodes.mesPacked.CODE_START)
        nodes.set_val(i,"s_command",nodes.mesPacked.dict_classif[nodes.mesPacked.CODE_START])
        nodes.set_val(i,"s_message",nodes.mesPacked.dict_classif[nodes.mesPacked.OK])
        nodes.set_val(i,"Objs",loadObjs(i,nodes))

    id_node=7
    id_nodeObj=0x1000+5
    i, i_obj=nodes.find_node_obj(id_node,id_nodeObj)
    if (i!=nodes.FIND_NODE_ERR and
        i_obj!=nodes.FIND_OBJ_ERR):
        nodes.mesPacked.print_message(nodes.list_nodes[i]["Objs"][i_obj], PLCGlobals.INFO)

    # nodes.print_list_nodes()

