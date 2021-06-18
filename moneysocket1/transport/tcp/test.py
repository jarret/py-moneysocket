# Copyright (c) 2021 Moneysocket Developers
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import asyncio
import threading

from .client_layer import TcpClientLayer
from .server_layer import TcpServerLayer

from ...layer import Layer
from ...nexus import Nexus

HOST = "localhost"
PORT = 9999


class TestTcpNexus(Nexus):
    def __init__(self, nexus):
        super().__init__(nexus, "TEST_TCP")


    def on_message(self, below_nexus, msg):
        print("got msg: %s" % msg)
        super().on_message(below_nexus, msg)

    def on_bin_message(self, below_nexus, msg_bytes):
        print("got bin: %s" % msg_bytes.hex())
        super().on_bin_message(below_nexus, msg_bytes)




class TestTcpClientLayer(Layer):
    def __init__(self):
        self.tcp_layer = TcpClientLayer()
        self.register_above_layer(self.tcp_layer)

    def announce_nexus(self, nexus):
        print("got: %s" % msg)
        test_nexus = TestTcpNexus(nexus)
        self._track_nexus(test_nexus, below_nexus)

        # start testing


class TestTcp():
    def __init__(self):
        self.server = None
        self.client = None


    async def run_client(self):
        t, p = await TcpClientLayer().connect2(HOST, PORT)
        print("client t: %s" % t)
        print("client p: %s" % p)

    async def run_server(self):
        self.server = await TcpServerLayer().listen_server(HOST, PORT)
        await asyncio.sleep(2)
        print("done")

    async def run(self):
        print("waiting")
        await asyncio.wait([self.run_server(), self.run_client()])
        print("waited")
        print("server close")
        self.server.close()
        print("server closed")
        return None


