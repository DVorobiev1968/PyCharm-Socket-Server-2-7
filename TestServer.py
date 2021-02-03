from unittest import TestCase
from Server import *
from Client import SocketClientApp

class ServerTestCase(TestCase):
    def test_Nodes(self):
        Nodes.test_Nodes()

    def test_node(self):
        SocketClientApp.test_node()

