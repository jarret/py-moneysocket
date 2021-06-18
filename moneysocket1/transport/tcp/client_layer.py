# Copyright (c) 2021 Moneysocket Developers
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import asyncio

from ..layer import ClientTransportLayer



class TcpClientProtocol(asyncio.Protocol):
    def __init__(self, layer):
        self.layer = layer
        self.message = "hello from client"

    def connection_made(self, transport):
        print("connection made call: %s" % transport)
        transport.write(self.message.encode())
        print('Data sent: {!r}'.format(self.message))
        #self.layer.announce_nexus("boof")

    def data_received(self, data):
        print('Data received: {!r}'.format(data.decode()))

    def connection_lost(self, exc):
        print('The server closed the connection')
        #self.layer.revoke_nexus("boof")

        # transport.close()?

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
        loop = asyncio.get_running_loop()
        print("client connecting:")
        transport, protocol = await loop.create_connection(
            lambda: TcpClientProtocol(self), host, port)
        print("got transport after connect: %s" % transport)
        # TODO - return future?
        # add task to event loop and carry on?
        return transport, protocol

    def new_nexus(self, nexus):
        print("announce: %s" % nexus)
        if self.onannounce:
            self.onanounce(nexus)

    def remove_nexus(self, nexus):
        print("revoke: %s" % nexus)
        if self.onrevoke:
            self.onrevoke(nexus)

