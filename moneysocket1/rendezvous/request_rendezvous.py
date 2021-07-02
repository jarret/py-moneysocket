# Copyright (c) 2021 Moneysocket Developers
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

from ..message.directory import MESSAGE_DIRECTORY
from ..message.request import Request

class RequestRendezvous(Request):
    SUBTYPE_NO = 0x1
    SUBTYPE_NAME = "RENDEZVOUS"
    def __init__(self, language_object, additional_tlvs=[],
                 sender_version=None):
        super().__init__(language_object, additional_tlvs=additional_tlvs,
                         sender_version=sender_version)

    @staticmethod
    def validate_subtype_data(language_object):
        print("SUBTYPE VALIDATE")
        # must have role
        # must have tiebreaker
        # must have rendezvous_id
        return None

    @staticmethod
    def new_message():
        lo = RequestRendezvous.new_language_object()
        return RequestRendezvous(lo)


MESSAGE_DIRECTORY.register(RequestRendezvous)
