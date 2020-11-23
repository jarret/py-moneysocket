# Copyright (c) 2020 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php
import logging
import uuid

from autobahn.twisted.websocket import WebSocketClientProtocol
from autobahn.twisted.websocket import WebSocketServerProtocol

from moneysocket.message.codec import MessageCodec


class IncomingSocket(WebSocketServerProtocol):
    def __init__(self):
        super().__init__()
        self.uuid = uuid.uuid4()

        self.onmessage = None
        self.onbinmessage = None

        self.was_announced = False

    def onConnecting(self, transport_details):
        logging.info("WebSocket connecting: %s" % transport_details)

    def onConnect(self, request):
        logging.info("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        logging.info("WebSocket connection open.")

        self.factory.ms_protocol_layer.announce_nexus(self)
        self.was_announced = True

    def onMessage(self, payload, isBinary):
        if isBinary:
            logging.info("binary payload: %d bytes" % len(payload))

            shared_seed = self.factory.ms_shared_seed

            if not shared_seed and MessageCodec.is_cyphertext(payload):
                if self.onbinmessage:
                    self.onbinmessage(self, payload)
                return
            msg, err = MessageCodec.wire_decode(payload,
                shared_seed=shared_seed)
            if err:
                logging.error("could not decode: %s" % err)
                return
            logging.info("recv msg: %s" % msg)
            if self.onmessage:
                self.onmessage(self, msg)
        else:
            logging.info("text payload: %s" % payload.decode("utf8"))
            logging.error("text payload is unexpected, dropping")

    def onClose(self, wasClean, code, reason):
        logging.info("WebSocket connection closed: {0}".format(reason))
        if self.was_announced:
            self.factory.ms_protocol_layer.revoke_nexus(self)

    ##########################################################################

    # stringify self like this a nexus

    def downward_iter_nexuses(self):
        # this is the bottom
        yield self

    def downline_str(self):
        return "\n".join([str(n) for n in self.downward_iter_nexuses()])

    def __str__(self):
        return "%-016s uuid: %s" % (self.__class__.__name__, self.uuid)

    ##########################################################################

    # Act like a nexus, but interface to WebSocket goo underneath

    def send(self, msg):
        logging.info("encoding msg: %s" % msg)
        shared_seed = self.factory.ms_shared_seed
        msg_bytes = MessageCodec.wire_encode(msg, shared_seed=shared_seed)
        self.send_bin(msg_bytes)

    def send_bin(self, msg_bytes):
        s = self.sendMessage(msg_bytes, isBinary=True)
        logging.info("sent message %d bytes, got: %s" % (len(msg_bytes), s))

    def initiate_close(self):
        super().sendClose()

    ##########################################################################

    def get_shared_seed(self):
        return self.factory.ms_shared_seed
