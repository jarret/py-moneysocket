# Copyright (c) 2021 Moneysocket Developers
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import asyncio
import uuid

from .nexus import TcpNexus


class TcpProtocol(asyncio.Protocol):
    def __init__(self, layer, shared_seed):
        self.uuid = uuid.uuid4()
        self.layer = layer
        self.transport = None
        self.onmessage = None
        self.onbinmessage = None
        self.shared_seed = shared_seed

    def connection_made(self, transport):
        message = "hello from server"
        self.transport = transport
        #transport.write(message.encode())
        self.layer.new_nexus(self)

    def data_received(self, data):
        print('Data received: {!r}'.format(data.decode()))
        if self.onbinmessage:
            self.onbinmessage(self, data.decode())

    def connection_lost(self, exc):
        self.layer.remove_nexus(self)
        print('The server closed the connection')

    ##########################################################################
    # provide nexus callins
    #########################################################################

    def send(self, msg):
        # encode
        self.transport.write(msg.encode_bin())

    def send_bin(self, msg_bytes):
        self.transport.write(msg_bytes)

    def initiate_close(self):
        self.transport.close()

    def get_shared_seed(self):
        return self.share_seed
