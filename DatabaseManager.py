#!/usr/bin/env python3
# encoding: utf-8
"""
DatabaseManager.py
This class handles saving the list of tweets and pruning it according to age.
"""

from ManagerBase import *
import sqlite3
import os
from typing import List
from GlobalSettings import *
from RSSItemTuple import *
import string


class DatabaseManager(ManagerBase):
    """
    This class abstracts our file management.

    pyTwittertoRSS keeps a list of tweet items that is converted into the RSS feed.  This class
    handles reading/writing the list as well as pruning the files based on age.
    """

    # *********************************************************************************************
    def __init__(self):
        """
        Constructor to initialize DatabaseManager
        """

        super().__init__()

        # Set this here so we can use it later
        self.printableChars = string.printable

        # If the DB is not there, create it
        if not os.path.exists(itemFilename):
            self.logger.info("Creating the database file {}".format(itemFilename))
            self.__CreateDatabaseFile()

    # *********************************************************************************************
    def __CreateDatabaseFile(self) -> bool:
        """
        Create the inital empty sqlite3 database to store past tweets

        :return: True if successful, False otherwise
        """

        try:
            sqlStr = 'CREATE TABLE rssitems (tweet_id integer PRIMARY KEY, tweet_url text, ' \
                     'user_name text, screen_name text, user_image_url text, tweet_text text, ' \
                     'found_urls text, created_at integer)'

            # Create our connection object
            tConnection = sqlite3.connect(itemFilename)
            tCursor = tConnection.cursor()

            # Create the items table
            tCursor.execute(sqlStr)

            # Commit changes and close
            tConnection.commit()
            tConnection.close()

            self.logger.info("Successfully created database file {}".format(itemFilename))

        except Exception as tExcept:
            self.logger.critical("*** DatabaseManager(__CreateDatabase): Could not create the database file!")
            self.logger.error(tExcept)
            return False

        return True

    # *********************************************************************************************
    def __EscapeSQLString(self, inString: str) -> str:
        """
        Change special characters in the string so we can push them into SQLITE3

        :param inString: String to fix
        :return: escaped string
        """

        if inString is None:
            return ""

        # Create a temp string by first removing everything not printable
        tempString = ''.join(filter(lambda x: x in self.printableChars, inString))

        return tempString.replace("'", "''")

    # *********************************************************************************************
    def GetHighestRead(self) -> int:
        """
        Get the highest tweet ID out of the database

        :return: Integer of the highest twitter ID
        """

        try:
            # Create our connections
            tConnection = sqlite3.connect(itemFilename)
            tCursor = tConnection.cursor()

            tCursor.execute("SELECT MAX(tweet_id) from rssitems")

            maxValue = tCursor.fetchone()

            tConnection.close()

        except Exception as tExcept:
            self.logger.critical("*** DatabaseManager(GetHighestRead): Unable to find the highest ID read!")
            self.logger.error(tExcept)
            return -1

        if maxValue[0] is None:
            return -1
        else:
            return maxValue[0]

    # *********************************************************************************************
    def PurgeOldEntries(self) -> bool:
        """
        Deletes entries older than purgeDays from the database

        :return: True if successful, False otherwise
        """

        try:
            # Create our connections
            tConnection = sqlite3.connect(itemFilename)
            tCursor = tConnection.cursor()

            # Create the query string and execute it
            queryString = "DELETE FROM rssitems WHERE datetime(created_at, 'unixepoch') <= " \
                          "datetime('now', '-{} hours', 'UTC')".format(purgeHours)
            tCursor.execute(queryString)

            # Commit changes and close
            tConnection.commit()
            tConnection.close()

        except Exception as tExcept:
            self.logger.warning("*** DatabaseManager(PurgeOldEntries): An error occurred while purging old data items")
            self.logger.error(tExcept)
            return False

        return True

    # *********************************************************************************************
    def ReadItems(self) -> List[RSSItemTuple]:
        """
        Reads old items from the database after purging those past our minimum age

        :return: True if successful, False otherwise
        """

        itemList = list()

        try:
            # First purge our old entries
            if not self.PurgeOldEntries():
                return list()

            # Create our connections
            tConnection = sqlite3.connect(itemFilename)
            tCursor = tConnection.cursor()

            # Get the rows
            tCursor.execute("SELECT * FROM rssitems ORDER BY created_at ASC")
            rows = tCursor.fetchall()

            # Loop through and enter into our list
            for row in rows:
                item = RSSItemTuple()

                item.tweet_id = row[0]
                item.tweet_url = row[1]
                item.user_name = row[2]
                item.screen_name = row[3]
                item.user_url = row[4]
                item.tweet_text = row[5]
                item.found_urls = row[6]
                item.created_at = datetime.datetime.fromtimestamp(row[7])

                itemList.append(item)

            # Close the connection
            tConnection.close()
        except Exception as tExcept:
            self.logger.critical("*** DatabaseManager(ReadItems): Unable to read in the items!")
            self.logger.error(tExcept)
            return list()

        return itemList

    # *********************************************************************************************
    def WriteNewItems(self, inItems: List[RSSItemTuple]) -> bool:
        """
        Writes new items into the database

        :return: True if successful, False otherwise
        """

        try:
            # Create our connections
            tConnection = sqlite3.connect(itemFilename)
            tCursor = tConnection.cursor()

            for item in inItems:
                # First fix our strings
                user_name = self.__EscapeSQLString(item.user_name)
                tweet_url = self.__EscapeSQLString(item.tweet_url)
                screen_name = self.__EscapeSQLString(item.screen_name)
                user_url = self.__EscapeSQLString(item.user_url)
                tweet_text = self.__EscapeSQLString(item.tweet_text)
                found_urls = self.__EscapeSQLString(item.found_urls)

                queryString = \
                    "INSERT INTO rssitems (tweet_id, tweet_url, user_name, screen_name, user_image_url, tweet_text, " \
                    "found_urls, created_at) VALUES ({tweetid}, '{tweeturl}', '{username}', '{screenname}', " \
                    "'{userurl}', '{tweettext}', '{foundurls}', {createdat})".format(tweetid=item.tweet_id,
                                                                                     tweeturl=tweet_url,
                                                                                     username=user_name,
                                                                                     screenname=screen_name,
                                                                                     userurl=user_url,
                                                                                     tweettext=tweet_text,
                                                                                     foundurls=found_urls,
                                                                                     createdat=int(
                                                                                         item.created_at.timestamp()))

                tCursor.execute(queryString)

            tConnection.commit()
            tConnection.close()

        except Exception as tExcept:
            self.logger.critical("*** DatabaseManager(WriteNewItems): Unable to write new items!")
            self.logger.error(tExcept)
            return False

        return True


# *************************************************************************************************
if __name__ == "__main__":
    foo = DatabaseManager()

    bar = foo.GetHighestRead()
