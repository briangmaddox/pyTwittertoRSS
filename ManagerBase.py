#!/usr/bin/env python3
# encoding: utf-8
"""
ManagerBase.py
Base class for the various Manager classes we use.
"""

import logging


class ManagerBase(object):
    """
    Base class for the various managers.
    """

    # ***********************************************************************************************
    def __init__(self):
        """
        Constructor to do shared initialization of the Managers
        """

        self.logger = logging.getLogger("pyTwittertoRSS")
