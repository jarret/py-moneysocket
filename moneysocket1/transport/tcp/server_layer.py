# Copyright (c) 2021 Moneysocket Developers
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import asyncio

from ..layer import ServerTransportLayer



class TcpServerProtocol(asyncio.Protocol):
    def __init__(self, layer):
        self.layer = layer
        self.message = "hello from server"

    def connection_made(self, transport):
        transport.write(self.message.encode())
        print('Data sent: {!r}'.format(self.message))
        #self.layer.announce_nexus("boof")

    def data_received(self, data):
        print('Data received: {!r}'.format(data.decode()))

    def connection_lost(self, exc):
        print('The server closed the connection')
        #self.layer.revoke_nexus("boof")

        # transport.close()?


class TcpServerLayer(ServerTransportLayer):
    def __init__(self):
        super().__init__()

    async def listen_server(self, host, port):
        loop = asyncio.get_running_loop()
        server = await loop.create_server(lambda: TcpServerProtocol(self),
                                          host, port)
        await server.start_serving()
        print("server: %s" % server)
        return server


    def new_nexus(self, nexus):
        print("announce: %s" % nexus)
        # create nexus
        # track nexus
        # layer event
        # announce

    def remove_nexus(self, nexus):
        print("revoke: %s" % nexus)
        self.revoke_nexus(nexus)
