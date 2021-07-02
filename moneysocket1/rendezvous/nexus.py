# Copyright (c) 2021 Moneysocket Developers
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import time
import os

from ..nexus import Nexus
from ..message.message import Message
from .request_rendezvous import RequestRendezvous

class Tiebreaker():
    def __init__(self, string=None, win=False, lose=False):
        if string is not None:
            self.value = bytes.fromhex(string)
        elif win:
            assert not lose, "cannot be set to win and lose"
            self.value = b'ffffffffffffffff'
        elif lose:
            self.value = b'0000000000000000'
        else:
            self.value = os.urandom(8)

    def __str__(self):
        return self.value.hex()




class RendezvousNexus(Nexus):
    def __init__(self, below_nexus, layer):
        super().__init__(below_nexus, layer)
        self.rendezvous_finished_cb = None
        self.tiebreaker = self.new_tiebreaker()

    def on_message(self, below_nexus, msg):
        print("Rendezvous nexus msg: %d" % len(msg))
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
            if msg.language_object['subtype'] == "NOTIFY_RENDEZVOUS":
                print("RENDEZVOUS: notify rendezvous")
                return
            elif (msg.language_object['subtype'] ==
                  "NOTIFY_RENDEZVOUS_NOT_READY"):
                print("RENDEZVOUS: notify rendezvous not ready")
                return
            elif msg.language_object['subtype'] == "NOTIFY_RENDEZVOUS_END":
                print("RENDEZVOUS: notify rendezvous end")
                return
        elif msg.language_object['type'] == "REQUEST":
            if msg.language_object['subtype'] == "REQUEST_RENDEZVOUS":
                print("RENDEZVOUS: rquest rendezvous")
                return
        super().on_message(below_nexus, msg_bytes)
        pass

    def on_message(self, below_nexus, msg):
        print("clear message")
        pass

    ###########################################################################


    ###########################################################################

    def start_rendezvous(self, rendezvous_finished_cb):
        print("START RENDEZVOUS")
        self.rendezvous_finished_cb = rendezvous_finished_cb
        self.tiebreaker = str(Tiebreaker())
        pass
