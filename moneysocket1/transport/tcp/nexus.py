# Copyright (c) 2021 Moneysocket Developers
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

from ...nexus import Nexus


class TcpNexus(Nexus):
    def __init__(self, below_nexus, layer):
        super().__init__(below_nexus, layer)

    def on_message():
        pass
