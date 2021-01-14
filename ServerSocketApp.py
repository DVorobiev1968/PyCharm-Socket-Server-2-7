# -*- coding: utf-8 -*-

import sys, getopt, socket, random
from threading import Thread, Lock
from time import sleep

from AlgoritmInfo import AlgoritmInfo
from MesPacked import MesPacked, NodeInfo
from PLCGlobals import PLCGlobals
from Nodes import Nodes


class ServerThread(Thread):
    """
    Базовый класс для предоставления сервисов управления потоками для приложения

    * lock: глобаный объект для управления блоктровками для глобальных переменных потоков
    * i_commandCode: глобальная переменная типа int задает код команды от клиента, с целью управления сессией клиента

    :param: * name: Имя потока
            * conn: Объект образуемый от sock.accept(), получаем коннект
            * addr: Адрес host

    """
    global nodes

    def __init__(self, name, conn, addr):
        """
        Иницилизируем необходимые св-ва класса:

        :param: name Имя потока
        :param: conn Объект образуемый от sock.accept(), получаем коннект
        :param: addr Адрес host

        :return: object Используемый при исполнении потока

        """
        Thread.__init__(self)
        self.name = name
        self.conn = conn
        self.addr = addr
        self.lock= Lock()
        self.i_commandCode=1

    def run(self):
        (caddr, cport) = self.addr
        mesPacked.print_message("Thread name:{0:s} has connection from {1:s}."
                                .format(str(self.name), caddr),
                                PLCGlobals.WARNING)

        mesPacked.print_message("Info nodes:{0}.".format(nodes.readInfoNodes()),PLCGlobals.INFO)
        stdin = self.conn.makefile("r")
        stdout = self.conn.makefile("w")
        self.parser(stdin, stdout)
        mesPacked.print_message("Thread {0:s} is done. i_codeCommand {1}.".
                                format(str(self.name), self.i_commandCode), PLCGlobals.WARNING)

    def loadObjs(self, index_node, nodes, nodeStruct):
        """
        Метод сохранения объекта в узле в краткосрочном хранилище

        :param: * index_node: индекс в списке узлов
                * nodes: объект - класс узел
                * nodeStruct: объект - класс узел, промежуточный для межсетевого обмена

        :return: список: list_nodes

        """
        i_status, list_obj = nodes.set_val_obj(nodes.list_nodes[index_node]['Objs'], nodeStruct)

        return list_obj

    def set_nodes(self, nodeStruct):
        """
        Метод сохраняет узел в краткосрочном хранилище через глобальную переменную nodes
        при сохранении заполняются все св-ва только класса NodeInfo

        :param nodeStruct: переменная со структурой узла

        """
        global nodes

        i_status, index = nodes.set_val(nodeStruct.i_idNode, "i_idNode", nodeStruct.i_idNode)
        i_status += nodes.mesPacked.CODE_NODES_OPERATION
        if nodeStruct.o_Algoritm.status==mesPacked.SET_ALGORITM_VAL_OK:
            nodes.set_val(nodeStruct.i_idNode, "i_code_answer", i_status)
        else:
            nodes.set_val(nodeStruct.i_idNode, "i_code_answer", nodeStruct.o_Algoritm.status)

        nodes.set_val(nodeStruct.i_idNode, "i_codeCommand", nodeStruct.i_codeCommand)
        nodes.set_val(nodeStruct.i_idNode, "s_command", nodes.mesPacked.dict_classif[nodeStruct.i_codeCommand])
        nodes.set_val(nodeStruct.i_idNode, "s_message", nodes.mesPacked.dict_classif[i_status])
        nodes.set_val(nodeStruct.i_idNode, "Algoritm", nodeStruct.o_Algoritm)

    def set_nodes_obj(self, nodeStruct):
        """
        Метод сохраняет узел в краткосрочном хранилище через глобальную переменную nodes
        при сохранении заполняются все св-ва классов NodeInfo, NodeInfoObj

        :param nodeStruct: переменная со структурой узла

        """
        global nodes

        i_status, index = nodes.set_val(nodeStruct.i_idNode, "i_idNode", nodeStruct.i_idNode)
        i_status += nodes.mesPacked.CODE_NODES_OPERATION
        if nodeStruct.o_Algoritm.status==mesPacked.SET_ALGORITM_VAL_OK:
            nodes.set_val(nodeStruct.i_idNode, "i_code_answer", i_status)
        else:
            nodes.set_val(nodeStruct.i_idNode, "i_code_answer", nodeStruct.o_Algoritm.status)

        nodes.set_val(nodeStruct.i_idNode, "i_codeCommand", nodeStruct.i_codeCommand)
        nodes.set_val(nodeStruct.i_idNode, "s_command", nodes.mesPacked.dict_classif[nodeStruct.i_codeCommand])
        nodes.set_val(nodeStruct.i_idNode, "s_message", nodes.mesPacked.dict_classif[i_status])
        nodes.set_val(nodeStruct.i_idNode, "Algoritm", nodeStruct.o_Algoritm)

        if i_status == PLCGlobals.ADD_OK or i_status == nodes.mesPacked.ADD_OK or \
                i_status == PLCGlobals.UPDATE_OK or i_status == nodes.mesPacked.UPDATE_OK:
            index = len(nodes.list_nodes) - 1
            nodes.set_val(nodeStruct.i_idNode, "Objs", self.loadObjs(index, nodes, nodeStruct))

    def save_node(self, i_status, nodeStruct):
        """
        Метод записывает данные по узлу и объекту в краткосрочный архив

        :param: * i_status: код ошибки получения ответа, его будем ассоциировать с i_code_answer
                * nodeStruct: объект с данными по узлу

        """
        if i_status == mesPacked.OK:
            self.set_nodes_obj(nodeStruct)
        else:
            self.set_nodes(nodeStruct)

    def parser(self, stdin, stdout):
        """
        метод обрабатывает входное сообщение от клиента и готовит ответ,
        при этом проверяя контрольную сумму
        пока от клиента не придет i_codeCommand=CODE_STOP

        :param: * stdin: буфферизированный входной поток для чтения данных из сокета
                * stdout: буфферизированный выходной поток для записи данных в сокет

        """

        data = stdin.readline()
        nodeStruct = NodeInfo()
        algoritm_status = mesPacked.SET_ALGORITM_VAL_OK
        while nodeStruct.i_codeCommand != mesPacked.CODE_EXIT:
            if algoritm_status == mesPacked.SET_ALGORITM_VAL_OK:
                i_status, nodeStruct = mesPacked.recvMessageNode(data)
                self.i_commandCode=nodeStruct.i_codeCommand

            if nodeStruct.i_codeCommand == mesPacked.CODE_SAVE_FOR_ALGORITM:
                nodeStruct.o_Algoritm.status=mesPacked.SET_ALGORITM_VAL_OK
                self.lock.acquire()
                self.save_node(i_status, nodeStruct)
                self.lock.release()
                nodeStruct.i_codeCommand = mesPacked.CODE_EXIT
                if i_status == mesPacked.OK:
                    mesPacked.print_message("CODE_SAVE_FOR_ALGORITM<-:{0}".format(nodeStruct.o_obj.b_message), PLCGlobals.BREAK_DEBUG)
                    mesPacked.setB_message(nodeStruct.o_Algoritm.status,nodeStruct)
                    stdout.write(nodeStruct.o_obj.s_message)
                    mesPacked.print_message("CODE_SAVE_FOR_ALGORITM->{0}".format(nodeStruct.o_obj.s_message), PLCGlobals.BREAK_DEBUG)
                else:
                    mesPacked.setB_message(i_status,nodeStruct)
                    stdout.write(nodeStruct.o_obj.s_message)
                    mesPacked.print_message("Error:CODE_SAVE_FOR_ALGORITM->{0}".format(nodeStruct.o_obj.s_message), PLCGlobals.ERROR)
                break

            if nodeStruct.i_codeCommand == mesPacked.CODE_LOAD_FOR_ALGORITM:
                i_node, i_obj = nodes.find_node_obj(nodeStruct.i_idNode, nodeStruct.o_obj.h_idObj)
                if (i_node != nodes.FIND_NODE_ERR and
                        i_obj != nodes.FIND_OBJ_ERR):
                    nodeStruct = mesPacked.setCommandNodeStruct(nodes.list_nodes[i_node]["i_codeCommand"],
                                                                mesPacked.SET_ALGORITM_WAIT,
                                                                nodes.list_nodes[i_node]["i_idNode"],
                                                                nodes.list_nodes[i_node]["Objs"][i_obj]["h_idObj"],
                                                                nodes.list_nodes[i_node]["Objs"][i_obj]["h_idSubObj"],
                                                                nodes.list_nodes[i_node]["Objs"][i_obj]["d_value"])
                nodeStruct.o_Algoritm=AlgoritmInfo(mesPacked.SET_ALGORITM_WAIT)
                self.lock.acquire()
                self.save_node(mesPacked.SET_ALGORITM_WAIT, nodeStruct)
                self.lock.release()
                if i_status == mesPacked.OK:
                    mesPacked.print_message("CODE_LOAD_FOR_ALGORITM:{0};id_Obj:{1:d}({1:4X})".
                                            format(nodeStruct.i_idNode,
                                                   nodeStruct.o_obj.h_idObj,
                                                   nodeStruct.o_Algoritm.status), PLCGlobals.INFO)

                    mesPacked.setB_message(nodeStruct.o_Algoritm.status,nodeStruct)
                    stdout.write(nodeStruct.o_obj.s_message)
                    mesPacked.print_message("CODE_LOAD_FOR_ALGORITM->{0}".format(nodeStruct.o_obj.s_message), PLCGlobals.BREAK_DEBUG)
                else:
                    mesPacked.setB_message(i_status,nodeStruct)
                    stdout.write(nodeStruct.o_obj.s_message)
                    mesPacked.print_message("Error:CODE_LOAD_FOR_ALGORITM->{0}".format(nodeStruct.o_obj.s_message), PLCGlobals.ERROR)
                nodeStruct.i_codeCommand = mesPacked.CODE_EXIT
                break
            elif nodeStruct.i_codeCommand == mesPacked.CODE_START:
                self.lock.acquire()
                self.save_node(i_status, nodeStruct)
                self.lock.release()
                if i_status == mesPacked.OK:
                    mesPacked.print_message("CODE_START<-:{0}".format(nodeStruct.o_obj.b_message), PLCGlobals.BREAK_DEBUG)
                    mesPacked.setB_message(i_status,nodeStruct)
                    stdout.write(nodeStruct.o_obj.s_message)
                    mesPacked.print_message("CODE_START->:{0}".format(nodeStruct.o_obj.s_message), PLCGlobals.BREAK_DEBUG)
                else:
                    mesPacked.setB_message(i_status,nodeStruct)
                    stdout.writeln(nodeStruct.o_obj.s_message)
                    mesPacked.print_message("Error in s_message:{0}".format(nodeStruct.o_obj.s_message), PLCGlobals.ERROR)
                data = stdin.readline()
            elif nodeStruct.i_codeCommand == mesPacked.CODE_SINGLE_START_SYNC:
                if i_status == mesPacked.OK:
                    nodeStruct.o_Algoritm = AlgoritmInfo(mesPacked.SET_ALGORITM_VAL_OK)
                    self.lock.acquire()
                    self.save_node(i_status, nodeStruct)
                    self.lock.release()
                    nodeStruct.i_codeCommand = mesPacked.CODE_EXIT
                    stdout.write(nodeStruct.o_obj.s_message)
                    mesPacked.print_message("CODE_SINGLE_START_SYNC->:{0}".format(nodeStruct.o_obj.s_message),
                                            PLCGlobals.BREAK_DEBUG)
                else:
                    mesPacked.setB_message(i_status, nodeStruct)
                    stdout.write(nodeStruct.o_obj.s_message)
                    mesPacked.print_message("Error:CODE_SINGLE_START_SYNC->:{0}".format(nodeStruct.o_obj.s_message),
                                            PLCGlobals.ERROR)
                break
            elif nodeStruct.i_codeCommand == mesPacked.CODE_SINGLE_START:
                if i_status == mesPacked.OK:
                    self.lock.acquire()
                    self.save_node(i_status, nodeStruct)
                    self.lock.release()
                    nodeStruct.i_codeCommand = mesPacked.CODE_EXIT
                    stdout.write(nodeStruct.o_obj.s_message)
                    mesPacked.print_message("CODE_SINGLE_START->{0}".format(nodeStruct.o_obj.s_message), PLCGlobals.BREAK_DEBUG)
                else:
                    mesPacked.setB_message(i_status,nodeStruct)
                    stdout.write(nodeStruct.o_obj.s_message)
                    mesPacked.print_message("Error:CODE_SINGLE_START->{0}".format(nodeStruct.o_obj.s_message), PLCGlobals.ERROR)
                break
            elif nodeStruct.i_codeCommand == mesPacked.CODE_LIST_NODES:
                mesPacked.print_message("Start listing nodes, recieve code:{0}...".format(nodeStruct.i_codeCommand),
                                        PLCGlobals.INFO)
                nodes.print_list_nodes()
                break
            elif nodeStruct.i_codeCommand == mesPacked.CODE_STOP:
                mesPacked.print_message("CODE_STOP:{0}...".format(nodeStruct.i_codeCommand),
                                        PLCGlobals.INFO)
                mesPacked.setCommandNodeStruct(mesPacked.CODE_STOP)
                stdout.write(nodeStruct.o_obj.s_message)
                mesPacked.print_message("CODE_STOP->:{0}".format(nodeStruct.o_obj.b_message), PLCGlobals.BREAK_DEBUG)
                break
            elif nodeStruct.i_codeCommand == mesPacked.CODE_EXIT:
                mesPacked.print_message("CODE_EXIT:{0}...".format(nodeStruct.i_codeCommand), PLCGlobals.INFO)
                mesPacked.setCommandNodeStruct(mesPacked.CODE_EXIT)
                stdout.write(nodeStruct.o_obj.s_message)
                mesPacked.print_message("CODE_EXIT->:{0}".format(nodeStruct.o_obj.b_message), PLCGlobals.BREAK_DEBUG)
                break
            elif nodeStruct.i_codeCommand == mesPacked.CODE_FIND_NODES:
                mesPacked.print_message("CODE_FIND_NODES:{0}, id_Obj:{1:d}({1:4X})".
                                        format(nodeStruct.i_idNode,
                                               nodeStruct.o_obj.h_idObj), PLCGlobals.INFO)
                i_node, i_obj = nodes.find_node_obj(nodeStruct.i_idNode, nodeStruct.o_obj.h_idObj)
                if (i_node != nodes.FIND_NODE_ERR and
                        i_obj != nodes.FIND_OBJ_ERR):
                    nodeStruct = mesPacked.setCommandNodeStruct(nodes.list_nodes[i_node]["i_codeCommand"],
                                                                mesPacked.SEARCH_OK,
                                                                nodes.list_nodes[i_node]["i_idNode"],
                                                                nodes.list_nodes[i_node]["Objs"][i_obj]["h_idObj"],
                                                                nodes.list_nodes[i_node]["Objs"][i_obj]["h_idSubObj"],
                                                                nodes.list_nodes[i_node]["Objs"][i_obj]["d_value"])
                    i_length, nodeStruct = mesPacked.setB_message(nodes.list_nodes[i_node]["i_codeCommand"], nodeStruct)
                else:
                    nodeStruct=mesPacked.setCommandNodeStruct(mesPacked.CODE_FIND_NODES, mesPacked.SEARCH_FAIL)
                    i_length, nodeStruct = mesPacked.setB_message(mesPacked.SEARCH_FAIL, nodeStruct)

                stdout.write(str(nodeStruct.o_obj.s_message))
                mesPacked.print_message("CODE_FIND_NODES->:{0}".format(nodeStruct.o_obj.s_message), PLCGlobals.BREAK_DEBUG)
                break
            elif nodeStruct.i_codeCommand == mesPacked.CODE_FIND_NODES_SYNC:
                mesPacked.print_message("CODE_FIND_NODES_SYNC:id_node:{0}, id_Obj:{1:d}({1:4X})".
                                        format(nodeStruct.i_idNode,
                                               nodeStruct.o_obj.h_idObj), PLCGlobals.INFO)
                i_node, i_obj = nodes.find_node_obj(nodeStruct.i_idNode, nodeStruct.o_obj.h_idObj)
                mesPacked.print_message("CODE_FIND_NODES_SYNC.find_node_obj:{0},{1}".
                                        format(i_node,i_obj), PLCGlobals.BREAK_DEBUG)
                if (i_node != nodes.FIND_NODE_ERR and
                        i_obj != nodes.FIND_OBJ_ERR):
                    i_code_answer=nodes.list_nodes[i_node]["Algoritm"].status
                    nodeStruct = mesPacked.setCommandNodeStruct(nodes.list_nodes[i_node]["i_codeCommand"],
                                                                i_code_answer,
                                                                nodes.list_nodes[i_node]["i_idNode"],
                                                                nodes.list_nodes[i_node]["Objs"][i_obj]["h_idObj"],
                                                                nodes.list_nodes[i_node]["Objs"][i_obj]["h_idSubObj"],
                                                                nodes.list_nodes[i_node]["Objs"][i_obj]["d_value"])
                    i_length, nodeStruct = mesPacked.setB_message(i_code_answer, nodeStruct)
                    mesPacked.print_message("CODE_FIND_NODES_SYNC.i_code_answer:{0}".
                                            format(i_code_answer), PLCGlobals.BREAK_DEBUG)
                    stdout.write(nodeStruct.o_obj.s_message)
                    mesPacked.print_message("CODE_FIND_NODES_SYNC.SET_ALGORITM_VAL_OK->:{0}".format(nodeStruct.o_obj.s_message),
                                            PLCGlobals.BREAK_DEBUG)
                    break
                else:
                    nodeStruct = mesPacked.setCommandNodeStruct(mesPacked.CODE_FIND_NODES, mesPacked.SEARCH_FAIL)
                    i_length, nodeStruct = mesPacked.setB_message(mesPacked.SEARCH_FAIL, nodeStruct)
                    stdout.write(str(nodeStruct.o_obj.s_message))
                    mesPacked.print_message("CODE_FIND_NODES_SYNC->s_message:{0}".format(nodeStruct.o_obj.s_message),
                                            PLCGlobals.WARNING)
            elif nodeStruct.i_codeCommand == mesPacked.CODE_EXIT_SERVER:
                mesPacked.print_message("CODE_EXIT_SERVER:{0}...".format(nodeStruct.i_codeCommand),
                                        PLCGlobals.INFO)
                mesPacked.nodeStruct.i_codeCommand = mesPacked.CODE_EXIT_SERVER
                break
            else:
                mesPacked.print_message("Else, recieve code:{0}...".format(nodeStruct.i_codeCommand),
                                        PLCGlobals.INFO)
                break


def loadSettings(key, mesPacked):
    if key == 1:
        if len(PLCGlobals.host) < 1:
            return "localhost"
        else:
            return PLCGlobals.host
    elif key == 2:
        if PLCGlobals.PORT < 1:
            return mesPacked.port
        else:
            return PLCGlobals.PORT
    else:
        pass


def main():
    global mesPacked
    mesPacked = MesPacked()
    try:
        opts, args = getopt.getopt(sys.argv[1:], "")
        if len(args) > 2:
            raise getopt.error("Too many arguments.")
    except getopt.error as msg:
        usage(msg)
    for o, a in opts:
        pass
    if args:
        try:
            host = args[0]
            port = int(args[1])
        except ValueError as msg:
            usage(msg)
    else:
        host = loadSettings(1, mesPacked)
        port = loadSettings(2, mesPacked)

    module = sys.argv[0].split('/')[-1].split('.')[0]
    sys_info = "Starting {0} from Python:{1}.{2}\n".format(module, sys.version_info.major, sys.version_info.minor)
    print (sys_info)
    main_thread(host, port)


def usage(msg=None):
    sys.stdout = sys.stderr
    if msg:
        print(msg)
    print("\n", __doc__)
    sys.exit(2)


def main_thread(host, port):
    global mesPacked, nodes
    nodes = Nodes()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(10)
    PLCGlobals.debug = PLCGlobals.BREAK_DEBUG
    mesPacked.print_message("Listening on port:{0:d}...".format(port), PLCGlobals.WARNING)

    while 1:
        (conn, addr) = sock.accept()
        if addr[0] != conn.getsockname()[0]:
            conn.close()
            mesPacked.print_message("Refusing connection from non-local host:{0:s}...".format(addr[0]),
                                    PLCGlobals.ERROR)
            continue
        name_thread = "ID:{0:d}".format(random.randint(1, 100))
        thread = ServerThread(name_thread, conn, addr)
        thread.start()

        # mesPacked.print_message("Close Thread:{1}({2}), recieve code:{0}.".
        #                         format(thread.i_commandCode, thread.name, thread.getName()),
        #                         PLCGlobals.INFO)
        if thread.i_commandCode == mesPacked.CODE_EXIT_SERVER:
            break
    del conn, addr

main()
