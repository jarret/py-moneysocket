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
    def __init__(self, nexus, layer):
        super().__init__(nexus, layer)


    def on_message(self, below_nexus, msg):
        print("got msg: %s" % msg)
        super().on_message(below_nexus, msg)

    def on_bin_message(self, below_nexus, msg_bytes):
        print("got bin: %s" % msg_bytes.hex())
        super().on_bin_message(below_nexus, msg_bytes)

    def send_ping(self):
        self.below_nexus.send_ping()


class TestTcpLayer(Layer):
    TCP_LAYER_CLASS = None
    def __init__(self):
        super().__init__()
        self.tcp_layer = self.TCP_LAYER_CLASS()
        self.register_above_layer(self.tcp_layer)
        self.tcp_layer.onpingresult = self.on_ping_result
        self.test_nexus = None
        self.test_below_nexus = None
        self.expects = []

    def announce_nexus(self, below_nexus):
        self.tcp_nexus = below_nexus
        self.test_nexus = TestTcpNexus(below_nexus, self)
        self.test_nexus.onmessage = self.on_message
        self.test_nexus.onbinmessage = self.on_bin_message

    def revoke_nexus(self, below_nexus):
        super().revoke_nexus(below_nexus)

    def check_expect(self, expect):
        wanted = self.expects.pop()
        assert wanted == expect

    def on_message(self, below_nexus, msg):
        pass

    def on_bin_message(self, below_nexus, msg_bytes):
        pass

    def on_ping_result(self, below_nexus, ping_secs):
        print("client layer got ping: %s" % ping_secs)
        self.check_expect("PING_RESULT")

    def send_ping(self):
        print("sending ping")
        self.test_nexus.send_ping()


class TestTcpClientLayer(TestTcpLayer):
    TCP_LAYER_CLASS = TcpClientLayer
    def __init__(self):
        super().__init__()

    async def connect(self, host, port):
        t, p = await self.tcp_layer.connect2(host, port)
        print("client t: %s" % t)
        print("client p: %s" % p)


class TestTcpServerLayer(TestTcpLayer):
    TCP_LAYER_CLASS = TcpServerLayer
    def __init__(self):
        super().__init__()

    async def listen_server(self, host, port):
        self.server = await self.tcp_layer.listen_server(host, port)

    def close_server(self):
        self.server.close()


class TestTcp():
    def __init__(self):
        self.test_server_layer = TestTcpServerLayer()
        self.test_client_layer = TestTcpClientLayer()


    async def connect_client(self):
        await self.test_client_layer.connect(HOST, PORT)
        print("client connected")

    async def start_server(self):
        await self.test_server_layer.listen_server(HOST, PORT)
        print("done")

    async def ping_from_client(self):
        self.test_client_layer.expects.append("PING_RESULT")
        self.test_client_layer.send_ping()

    async def ping_from_server(self):
        self.test_server_layer.expects.append("PING_RESULT")
        self.test_server_layer.send_ping()

    async def run_tests(self):
        await self.ping_from_client()
        await asyncio.sleep(0.2)
        assert len(self.test_client_layer.expects) == 0
        await self.ping_from_server()
        await asyncio.sleep(0.2)
        assert len(self.test_server_layer.expects) == 0

    async def run(self):
        print("setup")
        await asyncio.wait([self.start_server()])
        await asyncio.wait([self.connect_client()])

        print("run tests")
        await asyncio.wait([self.run_tests()])

        print("teardown")
        self.test_server_layer.close_server()
        return None


