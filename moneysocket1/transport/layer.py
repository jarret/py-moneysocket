# Copyright (c) 2021 Moneysocket Developers
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php


from ..layer import Layer

from .nexus import TransportNexus

class TransportLayer(Layer):
    def __init__(self):
        super().__init__()
        self.onpingresult = None

    def announce_nexus(self, below_nexus):
        transport_nexus = TransportNexus(below_nexus, self)
        transport_nexus.onpingresult = self.on_ping_result
        self._track_nexus(transport_nexus, below_nexus)
        self._track_nexus_announced(transport_nexus)
        self.send_layer_event(transport_nexus, "NEXUS_ANNOUNCED");
        if self.onannounce:
            self.onannounce(transport_nexus)

    def on_ping_result(self, nexus, ping_secs):
        if self.onpingresult:
            self.onpingresult(nexus, ping_secs)


class ClientTransportLayer(TransportLayer):
    def __init__(self):
        super().__init__()

    async def connect(self, beacon):
        raise NotImplementedError



class ServerTransportLayer(TransportLayer):
    def __init__(self):
        super().__init__()

    async def listen_server(self, *args, **kwargs):
        raise NotImplementedError
