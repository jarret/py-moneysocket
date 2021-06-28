# Copyright (c) 2021 Moneysocket Developers
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import time

from ..nexus import Nexus
from ..message.request.transport_ping import TransportPing
from ..message.notification.transport_pong import TransportPong
from ..message.message import Message


class TransportNexus(Nexus):
    def __init__(self, below_nexus, layer):
        super().__init__(below_nexus, layer)
        self.ping_send_time = None
        self.onpingresult = None

    def on_message(self, below_nexus, msg):
        print("Transport nexus msg: %d" % len(msg))
        super().on_message(below_nexus, msg)
        pass

    def on_bin_message(self, below_nexus, msg_bytes):
        print("Transport nexus bin msg: %d" % len(msg_bytes))
        msg, err = Message.decode_bytes(msg_bytes)
        if err:
            print("failed to decode, might be cyphertext: %s" % err)
            super().on_bin_message(below_nexus, msg_bytes)
            return

        if msg.language_object['type'] == "NOTIFICATION":
            if msg.language_object['subtype'] == "TRANSPORT_PONG":
                print("transport pong")
                if self.onpingresult and self.ping_send_time != None:
                    print("call pong result")
                    self.onpingresult(self, time.time() - self.ping_send_time)
                    return
        elif msg.language_object['type'] == "REQUEST":
            if msg.language_object['subtype'] == "TRANSPORT_PING":
                print("transport ping")
                self.send_pong()
                return
        super().on_bin_message(below_nexus, msg_bytes)
        pass

    def on_message(self, below_nexus, msg):
        print("clear message")
        pass

    def send_pong(self):
        print("sending pong")
        tp = TransportPong.new_message()
        self.send(tp)

    def send_ping(self):
        print("sending ping")
        self.ping_send_time = time.time()
        tp = TransportPing.new_message()
        self.send(tp)
