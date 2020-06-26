#!/usr/bin/env python3
# encoding: utf-8
"""
pyTwittertoRSS.py

Defines the main function of pyTwittertoRSS
"""
import datetime
import logging
import os
from TwitterManager import TwitterManager
from DatabaseManager import DatabaseManager
from FeedManager import FeedManager
from GlobalSettings import *


def main():
    myLogger = None
    try:
        # First, set up logging
        myLogger = logging.getLogger("pyTwittertoRSS")
        myLogger.setLevel(logging.DEBUG)

        # Set up the logger file handler
        myFileHandler = logging.FileHandler(logFilename)
        myFileHandler.setLevel(logging.DEBUG)

        # Set the formatting
        myFormatter = logging.Formatter('%(asctime)s - %(levelname)s - %(lineno)d - %(message)s',
                                        '%Y-%m-%d %I:%M:%S %p %Z')
        myFileHandler.setFormatter(myFormatter)
        myLogger.addHandler(myFileHandler)

    except Exception as tExcept:
        print("Could not set up logging. Exception was {}.".format(tExcept.__str__()))
        print("Exiting....")
        exit()

    try:
        myLogger.info("Now generating RSS feeds at {}".format(datetime.datetime.now()))
        # Create our file manager in case we have previous tweets
        myItemsFileManager = DatabaseManager()

        hightestRead = myItemsFileManager.GetHighestRead()

        myTwitterManager = TwitterManager(hightestRead)

        newTweets = myTwitterManager.GetTweets()

        # If we get rate limited, we won't be able to get anything back so only try if
        if newTweets is not None:
            myItemsFileManager.WriteNewItems(newTweets)

            myFeedManager = FeedManager()
            tweetsOut = myItemsFileManager.ReadItems()
            myFeedManager.WriteFeed(tweetsOut)

        myLogger.info("Finished generating feed at {}".format(datetime.datetime.now()))

        # Now copy it to the server
        os.system("scp {} {}".format(feedFilename, scpUserHost))
    except Exception as tExcept:
        myLogger.error(tExcept)
        myLogger.critical("An exception has occurred while trying to create the RSS feed!")
        exit()


if __name__ == "__main__":
    main()
