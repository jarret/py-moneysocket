# Copyright (c) 2021 Moneysocket Developers
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import asyncio

from ..layer import ClientTransportLayer
from .protocol import TcpProtocol
from ..nexus import TransportNexus


class TcpClientLayer(ClientTransportLayer):
    def __init__(self):
        super().__init__()

    def get_location(self, beacon):
        locations = [l for l in beacon.locations if
                     l.__class__ == TcpLocation]
        locations.sort(key=lambda l: l.generator_preference).reverse()
        return locations[0]

    async def connect(self, beacon):
        location = self.get_location(beacon)
        host = location.hostname
        port = location.port

        loop = asyncio.get_running_loop()

        transport, protocol = await loop.create_connection(
            lambda: TcpClientProtocol(self), host, port)
        # TODO - return future?
        # add task to event loop and carry on?

    async def connect2(self, host, port):
        shared_seed = "TODO: pull from beacon"
        loop = asyncio.get_running_loop()
        print("client connecting:")
        transport, protocol = await loop.create_connection(
            lambda: TcpProtocol(self, shared_seed), host, port)
        print("got transport after connect: %s" % transport)
        print("got protocol after connect: %s" % protocol.uuid)
        # TODO - return future?
        # add task to event loop and carry on?
        return transport, protocol
