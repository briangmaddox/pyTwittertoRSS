#!/usr/bin/env python3
# encoding: utf-8
"""
RSSItemTuple.py

Defines the class RSSItemTuple that contains the information for each feed item.
"""

import datetime


class RSSItemTuple(object):
    """
    This class simple holds the RSS entries that we are storing in the database.
    """

    def __init__(self):
        self.tweet_id = -1
        self.tweet_url = ""
        self.user_name = ""
        self.screen_name = ""
        self.user_url = ""
        self.tweet_text = ""
        self.found_urls = ""
        self.created_at = datetime.datetime.now()
