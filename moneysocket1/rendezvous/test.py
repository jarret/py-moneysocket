# Copyright (c) 2021 Moneysocket Developers
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import asyncio

from ..transport.tcp.client_layer import TcpClientLayer
from ..transport.tcp.server_layer import TcpServerLayer

from .layer import RendezvousLayer

from ..layer import Layer
from ..nexus import Nexus

HOST = "localhost"
PORT = 9999



class TestRendezvousNexus(Nexus):
    def __init__(self, nexus, layer):
        super().__init__(nexus, layer)

    def on_message(self, below_nexus, msg):
        print("got msg: %s" % msg)
        super().on_message(below_nexus, msg)

    def on_bin_message(self, below_nexus, msg_bytes):
        print("got bin: %s" % msg_bytes.hex())
        super().on_bin_message(below_nexus, msg_bytes)


class TestRendezvousLayer(Layer):
    TCP_LAYER_CLASS = None
    def __init__(self):
        super().__init__()
        self.tcp_layer = self.TCP_LAYER_CLASS()
        self.rendezvous_layer = RendezvousLayer()
        self.rendezvous_layer.register_above_layer(self.tcp_layer)
        self.register_above_layer(self.rendezvous_layer)

        self.test_nexus = None
        self.test_below_nexus = None

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



class TestRendezvousClientLayer(TestRendezvousLayer):
    TCP_LAYER_CLASS = TcpClientLayer
    def __init__(self):
        super().__init__()

    async def connect(self, host, port):
        t, p = await self.tcp_layer.connect2(host, port)


class TestRendezvousServerLayer(TestRendezvousLayer):
    TCP_LAYER_CLASS = TcpServerLayer
    def __init__(self):
        super().__init__()

    async def listen_server(self, host, port):
        self.server = await self.tcp_layer.listen_server(host, port)

    def close_server(self):
        self.server.close()




###############################################################################
#
###############################################################################

class TestRendezvous():
    def __init__(self):
        self.test_server_layer = TestRendezvousServerLayer()
        self.test_client_layer = TestRendezvousClientLayer()

    async def connect_client(self):
        await self.test_client_layer.connect(HOST, PORT)
        print("client connected")

    async def start_server(self):
        await self.test_server_layer.listen_server(HOST, PORT)
        print("done")

    async def run_tests(self):
        # TODO - send and receive clear message
        pass

    async def run(self):
        print("setup")
        await asyncio.wait([self.start_server()])
        await asyncio.wait([self.connect_client()])

        print("run tests")
        await asyncio.wait([self.run_tests()])

        print("teardown")
        self.test_server_layer.close_server()
        return None
