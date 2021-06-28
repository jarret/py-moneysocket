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
        self.ping_future = None
        self.ping_timer = None
        self.bin_message_future = None
        self.bin_message_timer = None
        self.bin_message_expected = None

    ###########################################################################

    def announce_nexus(self, below_nexus):
        self.tcp_nexus = below_nexus
        self.test_nexus = TestTcpNexus(below_nexus, self)
        self.test_nexus.onmessage = self.on_message
        self.test_nexus.onbinmessage = self.on_bin_message

    def revoke_nexus(self, below_nexus):
        super().revoke_nexus(below_nexus)

    ###########################################################################

    def on_message(self, below_nexus, msg):
        pass

    ###########################################################################

    def on_ping_result(self, below_nexus, ping_secs):
        print("client layer got ping: %s" % ping_secs)
        assert self.ping_future != None
        self.ping_future.set_result("PING_RESULT_OK")
        self.ping_timer.cancel()

    def ping_timeout(self):
        assert self.ping_future != None
        self.ping_future.set_result("PING_RESULT_TIMEOUT")

    def send_ping(self):
        loop = asyncio.get_running_loop()
        self.ping_future = loop.create_future()
        self.ping_timer = loop.call_later(1.0, self.ping_timeout)
        print("sending ping")
        self.test_nexus.send_ping()
        return self.ping_future

    ###########################################################################

    def on_bin_message(self, below_nexus, msg_bytes):
        print("test layer got: %s" % msg_bytes.hex())
        assert msg_bytes == self.bin_message_expected
        self.bin_message_future.set_result("BIN_MESSAGE_OK")
        self.bin_message_timer.cancel()

    def bin_message_timeout(self):
        assert self.bin_message_future != None
        self.bin_message_future.set_result("BIN_MESSAGE_TIMEOUT")

    def send_bin_message(self, msg_bytes):
        self.test_nexus.send_bin(msg_bytes)

    def expect_bin_message(self, msg_bytes):
        loop = asyncio.get_running_loop()
        self.bin_message_future = loop.create_future()
        self.bin_message_timer = loop.call_later(1.0, self.bin_message_timeout)
        self.bin_message_expected = msg_bytes
        print("sending msg_bytes")
        return self.bin_message_future


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


###############################################################################
# tcp client/server tests
###############################################################################

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

    async def run_tests(self):
        # send ping both ways
        fut = self.test_client_layer.send_ping()
        print("fut: %s" % fut)
        result = await fut
        assert result == "PING_RESULT_OK"

        fut = self.test_server_layer.send_ping()
        result = await fut
        assert result == "PING_RESULT_OK"

        # send cyphertext both ways
        fut = self.test_server_layer.expect_bin_message(b'deadbeef')
        self.test_client_layer.send_bin_message(b'deadbeef')
        result = await fut
        assert result == "BIN_MESSAGE_OK"

        fut = self.test_client_layer.expect_bin_message(b'beefdead')
        self.test_server_layer.send_bin_message(b'beefdead')
        result = await fut
        assert result == "BIN_MESSAGE_OK"

        # TODO - send and receive clear message

    async def run(self):
        print("setup")
        await asyncio.wait([self.start_server()])
        await asyncio.wait([self.connect_client()])

        print("run tests")
        await asyncio.wait([self.run_tests()])

        print("teardown")
        self.test_server_layer.close_server()
        return None


