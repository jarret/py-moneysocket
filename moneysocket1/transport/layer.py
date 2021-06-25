# Copyright (c) 2021 Moneysocket Developers
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php


from ..layer import Layer

class TransportLayer(Layer):
    def __init__(self):
        super().__init__()
        self.onpingresult = None


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
