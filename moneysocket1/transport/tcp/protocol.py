# Copyright (c) 2021 Moneysocket Developers
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php


import asyncio
import uuid

from ...message.message import Message


class TcpProtocol(asyncio.Protocol):
    # Adapts tcp prococol to nexus behavior.
    # Behaves like a nexus, but doesn't inherit.
    def __init__(self, layer, shared_seed):
        self.uuid = uuid.uuid4()
        self.layer = layer
        self.transport = None
        self.onmessage = None
        self.onbinmessage = None
        self.shared_seed = shared_seed

    def connection_made(self, transport):
        message = "hello from server"
        self.transport = transport
        #transport.write(message.encode())
        self.layer.announce_nexus(self)

    def data_received(self, data):
        print('Data received: %s' % data.hex())
        if not self.onbinmessage:
            return
        clear_msg, remainder = Message.pop_clear_message(data)
        if clear_msg != None:
            print("clear: %s" % clear_msg.hex())
            print("remainder: %s" % remainder.hex())
            # if there is a cleartext message, we can chop it off and pass up
            self.onbinmessage(self, clear_msg)
            # do this again for any remainder in case messages are
            # concatenated
            if len(remainder) > 0:
                self.data_received(remainder)
        else:
            # if there is nothing to be understood, it might be cyphertext,
            # so pass upwards as-is
            self.onbinmessage(self, data)

    def connection_lost(self, exc):
        self.layer.revoke_nexus(self)
        print('The server closed the connection')

    ##########################################################################
    # provide nexus callins
    #########################################################################

    def send(self, msg):
        # encode
        m = msg.encode_bytes()
        print("tcp nexus send: %d" % len(m))
        self.transport.write(m)

    def send_bin(self, msg_bytes):
        print("tcp nexus send bin: %d" % len(msg_bytes))
        self.transport.write(msg_bytes)

    def initiate_close(self):
        self.transport.close()

    def get_shared_seed(self):
        return self.share_seed
