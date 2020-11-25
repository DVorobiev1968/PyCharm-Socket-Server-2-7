# -*- coding: utf-8 -*-
import copy, random
from switch import switch
from PLCGlobals import PLCGlobals
from MesPacked import MesPacked

class Objs:
    messageErr=""
    def __init__(self):
        key = ['h_idObj',
               'h_idSubObj',
               'i_typeData',
               'd_value',
               'i_check',
               'b_message']
        value = [0x0,
                 0x0,
                 0,
                 0.0,
                 0,
                 bytes()]
        self.dict_objs = dict(zip(key, value))
        self.list_objs = []
        self.mesPacked=MesPacked()

    def __del__(self):
        pass

    def set_dict_val(self, key, value):
        b_status = False
        if self.dict_objs.get(key) is not None:
            self.dict_objs[key] = value
            b_status = True
        return b_status

    def add_item_dict(self, key, item):
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

    def get_val(self, id_Obj, name_field):
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

    def set_val(self, id_Obj, name_field, value=0):
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
                        self.list_objs[i]["i_check"] = self.mesPacked.set_CRC()
                        i_status = PLCGlobals.SET_VAL_OK
                        break
        if i_status == PLCGlobals.SET_VAL_FAIL and "h_idObj" in name_field:
            self.set_dict_val("h_idObj", value)
            self.add_item_objs(self.dict_objs)
        return i_status

    def find_obj(self, id_obj):
        length = len(self.list_objs)
        for i in range(length):
            if self.list_objs[i]["h_idObj"]==id_obj:
                return True, self.list_objs[i]
        return False, None

    def print_dict_objs(self):
        self.mesPacked.print_message(self.dict_objs,PLCGlobals.INFO)

    def print_list_obj(self):
        length = len(self.list_objs)
        for i in range(length):
            self.mesPacked.print_message(self.list_objs[i],PLCGlobals.INFO)

class Nodes():
    messageErr=""
    mesPacked=MesPacked()

    def __init__(self):

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
                 None]
        self.dict_nodes = dict(zip(key, value))
        self.list_nodes = []

    def __del__(self):
        pass

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
                        self.list_nodes[i]["Obj"]=value
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
                return True, self.list_nodes[i]
        return False, None

    def print_dict_nodes(self):
        self.mesPacked.print_message(self.dict_nodes,PLCGlobals.INFO)

    def print_list_nodes(self):
        length = len(self.list_nodes)
        for i in range(length):
            self.mesPacked.print_message(self.list_nodes[i],PLCGlobals.INFO)
            len_objs=len(self.list_nodes[i]["Obj"].list_objs)
            self.messageErr="Obj:{0:3d}".format(len_objs)
            self.mesPacked.print_message(self.messageErr,PLCGlobals.INFO)
            for j in range(len_objs):
                 self.mesPacked.print_message(self.list_nodes[i]["Obj"].list_objs[j], PLCGlobals.INFO)

################################ start section #################################
def loadObjs(id_node,objs):
    # тестируем объекты в узлах
    for i in range(1, 10):
        h_idObj=0x1000+i
        h_idSubObj=0x0
        d_value=random.random()
        objs.set_val(h_idObj,"h_idObj",h_idObj)
        objs.set_val(h_idObj,"h_idSubObj",h_idSubObj)
        objs.set_val(h_idObj,"i_typeData",objs.mesPacked.dict_typeData["Float"])
        objs.set_val(h_idObj,"d_value",d_value)
        # objs.mesPacked.initNodeStruct(id_node,h_idObj,h_idSubObj,d_value)
        # objs.set_val(h_idObj, "b_message")
        # objs.set_val(h_idObj, "i_check")
    return objs

if __name__ == '__main__':
    global debug

    messageErr = "py_runtime start..."

    nodes = Nodes()

    # тестируем узлы
    for i in range(1, 10):
        i_status=nodes.set_val(i,"i_idNode",i)
        nodes.set_val(i,"i_code_answer",nodes.mesPacked.OK)
        nodes.set_val(i,"i_codeCommand",nodes.mesPacked.CODE_START)
        nodes.set_val(i,"s_command",nodes.mesPacked.dict_classif[nodes.mesPacked.CODE_START])
        nodes.set_val(i,"s_message",nodes.mesPacked.dict_classif[nodes.mesPacked.OK])
        if (i_status==PLCGlobals.ADD_OK):
            obj = Objs()
            nodes.set_val(i,"Objs",loadObjs(i,obj))

    id_node=7
    id_nodeObj=0x1000+5
    b_status, list_nodes=nodes.find_node(id_node)
    if (b_status):
        b_status_obj, list_objs=list_nodes['Obj'].find_obj(id_nodeObj)
        if (b_status_obj):
            print list_objs


    nodes.print_list_nodes()

