# Copyright (c) 2021 Moneysocket Developers
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import asyncio

from ..layer import ServerTransportLayer

from .protocol import TcpProtocol
from ..nexus import TransportNexus


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

    def announce_nexus(self, below_nexus):
        print("server announce nexus: %s" % below_nexus)
        transport_nexus = TransportNexus(below_nexus, self)
        transport_nexus.onpingresult = self.on_ping_result
        self._track_nexus(transport_nexus, below_nexus)
        self._track_nexus_announced(transport_nexus)
        self.send_layer_event(transport_nexus, "NEXUS_ANNOUNCED");
        if self.onannounce:
            self.onannounce(transport_nexus)

    def on_ping_result(self, nexus, ping_secs):
        print("got server layer ping result")
        if self.onpingresult:
            print("server layer ping result")
            self.onpingresult(nexus, ping_secs)

