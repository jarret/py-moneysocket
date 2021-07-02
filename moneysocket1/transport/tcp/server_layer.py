# Copyright (c) 2021 Moneysocket Developers
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import asyncio

from ..layer import ServerTransportLayer

from .protocol import TcpProtocol


class TcpServerLayer(ServerTransportLayer):
    def __init__(self):
        super().__init__()
        self.shared_seed = None

    async def listen_server(self, host, port):
        loop = asyncio.get_running_loop()
        server = await loop.create_server(lambda: TcpProtocol(self, None),
                                          host, port)
        await server.start_serving()
        print("server: %s" % server)
        return server
