#!/usr/bin/env python3
# encoding: utf-8
"""
TwitterManager.py

This class handles interactions with Twitter via Tweepy.
"""

from ManagerBase import ManagerBase
from typing import List
import tweepy
from GlobalSettings import *
from RSSItemTuple import *


class TwitterManager(ManagerBase):
    """
    Class to abstract interactions with the Twitter API
    """

    # *********************************************************************************************
    def __init__(self, inLastID=-1):
        """
        Construct our object.
        """
        try:
            super().__init__()

            # Set up the Tweepy OAuth object
            self.auth = tweepy.OAuthHandler(twitter_credentials["consumerKey"],
                                            twitter_credentials["consumerSecret"])
            self.auth.set_access_token(twitter_credentials["accessToken"],
                                       twitter_credentials["accessTokenSecret"])

            # Now create the Tweepy API object
            self.tweepyAPI = tweepy.API(self.auth)

            self.logger.info("Successfully create the Tweepy API object.")

            self.lastID = inLastID
            self.logger.info("Setting the last id to {}.".format(inLastID))

        except Exception as tExcept:
            self.logger.critical("*** TwitterManager.py(__init__): Could not create our Tweepy API object! Exiting....")
            self.logger.error(tExcept)
            exit()

    # *********************************************************************************************
    def __CreateTweetURL(self, inTweet: tweepy.models.Status) -> str:
        """
        Generate the URL of the tweet for storage
        :param inTweet: Tweet object
        :return: string of the url
        """

        outString = "http://www.twitter.com/{screenname}/status/{idstr}". \
            format(screenname=inTweet.user.screen_name,
                   idstr=inTweet.id_str)

        return outString

    # *********************************************************************************************
    def __CreateTweetItem(self, inTweet: tweepy.models.Status) -> RSSItemTuple:
        """
        Parse out the tweet elements we need and return them
        :param inTweet: individual tweet from Tweepy
        :return: RSSItemTuple
        """
        try:
            item = RSSItemTuple()

            item.tweet_id = inTweet.id
            item.tweet_url = self.__CreateTweetURL(inTweet)
            item.user_name = inTweet.user.name
            item.user_url = inTweet.user.url
            item.screen_name = inTweet.user.screen_name
            item.tweet_text = inTweet.text

            # Pull out any URLs from the tweet and add them.
            for url in inTweet.entities['urls']:
                item.found_urls += url['expanded_url']
                item.found_urls += ", "

            item.created_at = inTweet.created_at

            return item
        except Exception as tExcept:
            self.logger.critical(
                "*** TwitterManager(__CreateTweetItem): Unable to parse the tweet {}".format(inTweet.text))
            self.logger.error(tExcept)
            return RSSItemTuple()

    # *********************************************************************************************
    def GetTweets(self) -> List[RSSItemTuple]:
        """
        Gets the list of new tweets.  If no lastID has been set, gets 500 tweets.
        :return: List of RSSItemTuples
        """
        itemList = list()
        item = RSSItemTuple()

        try:
            if self.lastID == -1:
                # Grab the first numberTweets tweets
                retTweets = self.tweepyAPI.home_timeline(count=numberTweets)

                for tweet in retTweets:
                    item = self.__CreateTweetItem(tweet)
                    itemList.append(item)

                self.logger.info("Successfully retrieved {} tweets.".format(len(itemList)))

                return itemList

            for tweet in tweepy.Cursor(self.tweepyAPI.home_timeline, since_id=str(self.lastID)).items():
                item = self.__CreateTweetItem(tweet)
                itemList.append(item)

            self.logger.info("Successfully retrieved {} tweets.".format(len(itemList)))

            return itemList

        except Exception as tExcept:
            self.logger.critical("*** TwitterManager(GetTweets): Unable to retrieve any tweets!")
            self.logger.error(tExcept)
            return list()


if __name__ == "__main__":
    foo = TwitterManager()

    tweets = foo.GetTweets()
