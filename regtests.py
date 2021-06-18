#!/usr/bin/env python3
# Copyright (c) 2021 Moneysocket Developers
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import asyncio
import sys

from moneysocket1.transport.tcp.test import TestTcp

TESTS = [TestTcp()]

if __name__ == '__main__':
    for test in TESTS:
        loop = asyncio.get_event_loop()
        err = loop.run_until_complete(test.run())
        print("ran:")
        if err:
            print(err)
            sys.exit(err)
