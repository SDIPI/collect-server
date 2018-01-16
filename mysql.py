#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This file is part of wdf-server.
"""
from typing import List, Tuple

import pymysql as pymysql

# Collect SQL
pageviewSQL = 'INSERT IGNORE INTO pageviews (wdfId, url, timestamp) VALUES (%s, %s, CURRENT_TIMESTAMP)'
pagerequestSQL = 'INSERT INTO pagerequests (wdfId, url, timestamp, request, method, size, urlDomain, requestDomain) VALUES (%s, %s, CURRENT_TIMESTAMP, %s, %s, %s, %s, %s)'
pageeventSQL = 'INSERT INTO `event` (wdfId, url, type, `value`) VALUES (%s, %s, %s, %s)'
contentSQL = 'INSERT INTO `content` (wdfId, url, timestamp, `content`, `language`, `title`) VALUES (%s, %s, CURRENT_TIMESTAMP, %s, %s, %s)'
watcheventSQL = 'INSERT INTO `pagewatch` (wdfId, url, timestamp, amount) VALUES (%s, %s, CURRENT_TIMESTAMP, %s)'
contentTextSQL = 'INSERT IGNORE INTO `content_text` (url, `content`, `title`, `language`) VALUES (%s, %s, %s, %s)'

# Collect Server SQL
getUsersSQL = 'SELECT * FROM `users`'
getContentsTextSQL = 'SELECT * FROM `content_text`'
getLastDayContentsSQL = 'SELECT `id`, `wdfId`, `url`, `timestamp` FROM `content` WHERE url LIKE CONCAT(\'%s\', \'%%\') AND timestamp >= DATE_ADD(NOW(), INTERVAL -1 DAY)'

newuserSQL = 'INSERT INTO users (wdfId, facebookAccessToken, wdfToken) VALUES ("%s", "%s", "%s")'
newOrUpdateuserSQL = "INSERT INTO users (facebookId, facebookAccessToken, wdfToken) VALUES (%(fbId)s, %(fbToken)s, %(wdfToken)s) ON DUPLICATE KEY UPDATE facebookId = %(fbId)s, facebookAccessToken = %(fbToken)s, wdfToken = %(wdfToken)s"

newAnonuserSQL = "INSERT INTO users (wdfToken) VALUES (%s)"
getUserFromTokenSQL = "SELECT * FROM `users` WHERE `wdfToken` = %s"

# Compute SQL
emptyTfTableSQL = "TRUNCATE computed_tf"
emptyDfTableSQL = "TRUNCATE computed_df"
emptyTfIdfTableSQL = "TRUNCATE computed_tfidf"
emptyBestWordsTableSQL = "TRUNCATE computed_bestwords"

tfSQL = 'INSERT IGNORE INTO `computed_tf` (url, word, tf) VALUES (%s, %s, %s)'
tfIdfSQL = 'INSERT IGNORE INTO `computed_tfidf` (url, word, tfidf) VALUES (%s, %s, %s)'
dfSQL = 'INSERT IGNORE INTO `computed_df` (word, df) VALUES (%s, %s)'

computeBestWordsSQL = '''SET @currcount = NULL, @currvalue = NULL;
INSERT INTO computed_bestwords
    SELECT url, word, tfidf FROM (
        SELECT
    url, word, tfidf,
    @currcount := IF(@currvalue = url, @currcount + 1, 1) AS rank,
    @currvalue := url AS whatever
    FROM computed_tfidf
    ORDER BY url, tfidf DESC
    ) AS whatever WHERE rank <= 20'''

# Interface SQL
mostVisitedSitesTemplateSQL1 = 'SELECT url, COUNT(*) AS count FROM `pageviews` WHERE `wdfId`=%s'
mostVisitedSitesTemplateSQL2 = ' GROUP BY `url` LIMIT 200'
mostWatchedSitesTemplateSQL1 = 'SELECT `wdfId`, `url`, CAST(SUM(`amount`) AS UNSIGNED) AS time FROM `pagewatch` WHERE wdfId=%s'
mostWatchedSitesTemplateSQL2 = ' GROUP BY wdfId, url ORDER BY SUM(`amount`) DESC LIMIT 200'

oldestEntrySQL = 'SELECT DATE(`timestamp`) AS date FROM `pageviews` WHERE `wdfId`=%s ORDER BY `timestamp` ASC LIMIT 1'

historySitesSQL = """
SELECT
`wdfId`,
`url`, DATE(timestamp) AS day,
CAST(SUM(`amount`) as UNSIGNED) AS sumAmount
FROM `pagewatch`
WHERE `wdfId` = %s
GROUP BY `url`, DATE(timestamp)
ORDER BY DATE(timestamp) ASC, SUM(`amount`) DESC"""

historySitesTemplateSQL1 = """
SELECT
`wdfId`,
`url`, DATE(timestamp) AS day,
CAST(SUM(`amount`) as UNSIGNED) AS sumAmount
FROM `pagewatch`
WHERE `wdfId` = %s"""

historySitesTemplateSQL2 = """
GROUP BY `url`, DATE(timestamp)
ORDER BY DATE(timestamp) ASC, SUM(`amount`) DESC"""

nbDocumentsSQL = "SELECT COUNT(*) AS `count` FROM (SELECT DISTINCT url FROM `computed_tf`) AS `cnt`"

tfIDfForUserSQL = """
SELECT *
FROM `computed_tfidf`
WHERE
`computed_tfidf`.`url` IN (SELECT DISTINCT url FROM `pageviews` WHERE `wdfId`=%s)
ORDER BY `url` DESC, `tfidf` DESC"""

bestWordsSQL = """SELECT * FROM `computed_bestwords`"""

interestsListSQL = """SELECT * FROM `interests`"""

cleanUserInterestsSQL = """DELETE FROM `user_interests` where user_id = %s"""
addUserInterestSQL = """INSERT IGNORE INTO `user_interests` (user_id, interest_id) VALUES (%s, %s)"""
getUserInterestsSQL = """SELECT * FROM `user_interests` WHERE user_id = %s"""

setUrlTopicSQL = """INSERT INTO `url_topics` (url, topic) VALUES (%s, %s)"""
getUrlsTopicSQL = """SELECT * FROM `url_topics`"""
emptyUrlTopicSQL = """TRUNCATE url_topics"""

setLdaTopicSQL = """INSERT INTO `lda_topics` (`topic_id`, `word`, `value`) VALUES (%s, %s, %s)"""
getLdaTopicsSQL = """SELECT * FROM `lda_topics`"""
emptyLdaTopicsSQL = """TRUNCATE lda_topics"""

setUserTagSQL = """REPLACE INTO `user_tags` (user_id, interest_id, word) VALUES (%s, %s, %s)"""
getUserTagsSQL = """SELECT * FROM `user_tags` WHERE user_id = %s"""

class MySQL:
    def __init__(self, host, user, password, dbname='connectserver'):
        self.host = host
        self.user = user
        self.password = password
        self.dbname = dbname
        self.typeName = {}

    def __enter__(self):
        self.db = pymysql.connect(host=self.host,
                             user=self.user,
                             password=self.password,
                             db=self.dbname,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
        self.db.connect()
        return self

    def __exit__(self, type, value, traceback):
        self.db.close()

    # Public methods

    def pageView(self, wdfId, url):
        with self.db.cursor() as db:
            db.execute(pageviewSQL, (wdfId, url))
        self.db.commit()

    def pageRequest(self, wdfId, url, request, method, size, urlDomain, requestDomain):
        with self.db.cursor() as db:
            db.execute(pagerequestSQL, (wdfId, url, request, method, size, urlDomain, requestDomain))
        self.db.commit()

    def pageEvent(self, wdfId, url, eventType, value):
        with self.db.cursor() as db:
            db.execute(pageeventSQL, (wdfId, url, eventType, value))
        self.db.commit()

    def watchEvents(self, wdfId, urls):
        list = []
        for url in urls:
            list.append((wdfId, url, urls[url]))
        with self.db.cursor() as db:
            db.executemany(watcheventSQL, list)
        self.db.commit()

    def content(self, wdfId, url, content, lang, title):
        with self.db.cursor() as db:
            db.execute(contentSQL, (wdfId, url, content, lang, title))
        self.db.commit()

    def newUser(self, wdfId, fbToken, wdfToken):
        with self.db.cursor() as db:
            db.execute(newuserSQL, (wdfId, fbToken, wdfToken))
        self.db.commit()

    def newOrUpdateUser(self, fbId, fbToken, wdfToken):
        with self.db.cursor() as db:
            db.execute(newOrUpdateuserSQL, {'fbId': int(fbId), 'fbToken': fbToken, 'wdfToken': wdfToken})
        self.db.commit()

    def newAnonUser(self, wdfToken):
        with self.db.cursor() as db:
            db.execute(newAnonuserSQL, (wdfToken))
        self.db.commit()

    def getUserWithToken(self, wdfToken):
        with self.db.cursor(pymysql.cursors.DictCursor) as db:
            db.execute(getUserFromTokenSQL)
            return db.fetchone()

    def getUsers(self):
        with self.db.cursor(pymysql.cursors.DictCursor) as db:
            db.execute(getUsersSQL)
            return db.fetchall()

    def getContentsText(self):
        with self.db.cursor(pymysql.cursors.DictCursor) as db:
            db.execute(getContentsTextSQL)
            return db.fetchall()

    def getLastDayContents(self, url):
        with self.db.cursor(pymysql.cursors.DictCursor) as db:
            db.execute(getLastDayContentsSQL % (url))
            return db.fetchall()

    def emptyTfDf(self):
        with self.db.cursor() as db:
            db.execute(emptyTfTableSQL)
            db.execute(emptyDfTableSQL)
            db.execute(emptyTfIdfTableSQL)
            db.execute(emptyBestWordsTableSQL)
        self.db.commit()

    def emptyUrlsTopic(self):
        with self.db.cursor() as db:
            db.execute(emptyUrlTopicSQL)
        self.db.commit()

    def setUrlsTopic(self, urlsTopic):
        with self.db.cursor() as db:
            db.executemany(setUrlTopicSQL, urlsTopic)
        self.db.commit()

    def emptyLdaTopics(self):
        with self.db.cursor() as db:
            db.execute(emptyLdaTopicsSQL)
        self.db.commit()

    def setLdaTopics(self, ldaTopics):
        with self.db.cursor() as db:
            db.executemany(setLdaTopicSQL, ldaTopics)
        self.db.commit()

    def setTf(self, tfs):
        list = []
        for url in tfs:
            words = tfs[url]
            for word in words:
                list.append((url, word, words[word]))
        with self.db.cursor() as db:
            db.executemany(tfSQL, list)
        self.db.commit()

    def setTfIdf(self, tfidfs):
        list = []
        for url in tfidfs:
            words = tfidfs[url]
            for word in words:
                list.append((url, word, words[word]))
        with self.db.cursor() as db:
            db.executemany(tfIdfSQL, list)
        self.db.commit()

    def setDf(self, dfs):
        list = []
        for word in dfs:
            df = dfs[word]
            list.append((word, df))
        with self.db.cursor() as db:
            db.executemany(dfSQL, list)
        self.db.commit()

    def setContentText(self, url, text, title, language):
        with self.db.cursor() as db:
            db.execute(contentTextSQL, (url, text, title, language))
        self.db.commit()

    def getMostVisitedSites(self, wdfId, fromArg, toArg):
        with self.db.cursor(pymysql.cursors.DictCursor) as db:
            timeConditions = self.__timeCondition(fromArg, toArg)
            query = mostVisitedSitesTemplateSQL1 + timeConditions + mostVisitedSitesTemplateSQL2
            db.execute(query, (wdfId))
            return db.fetchall()

    def getMostWatchedSites(self, wdfId, fromArg, toArg):
        with self.db.cursor(pymysql.cursors.DictCursor) as db:
            timeConditions = self.__timeCondition(fromArg, toArg)
            query = mostWatchedSitesTemplateSQL1 + timeConditions + mostWatchedSitesTemplateSQL2
            db.execute(query, (wdfId))
            return db.fetchall()

    def getBestWords(self):
        with self.db.cursor(pymysql.cursors.DictCursor) as db:
            db.execute(bestWordsSQL)
            return db.fetchall()

    def getNbDocuments(self):
        with self.db.cursor(pymysql.cursors.DictCursor) as db:
            db.execute(nbDocumentsSQL)
            return db.fetchone()

    def getHistorySites(self, wdfId, fromArg, toArg):
        with self.db.cursor(pymysql.cursors.DictCursor) as db:
            timeConditions = self.__timeCondition(fromArg, toArg)
            query = historySitesTemplateSQL1 + timeConditions + historySitesTemplateSQL2
            db.execute(query, (wdfId))
            return db.fetchall()

    def getOldestEntry(self, wdfId):
        with self.db.cursor(pymysql.cursors.DictCursor) as db:
            db.execute(oldestEntrySQL, (wdfId))
            return db.fetchone()

    def getUrlsTopic(self):
        with self.db.cursor(pymysql.cursors.DictCursor) as db:
            db.execute(getUrlsTopicSQL)
            return db.fetchall()

    def getLdaTopics(self):
        with self.db.cursor(pymysql.cursors.DictCursor) as db:
            db.execute(getLdaTopicsSQL)
            return db.fetchall()

    def getInterestsList(self):
        with self.db.cursor(pymysql.cursors.DictCursor) as db:
            db.execute(interestsListSQL)
            return db.fetchall()

    def cleanUserInterests(self, wdfId):
        with self.db.cursor(pymysql.cursors.DictCursor) as db:
            db.execute(cleanUserInterestsSQL, (wdfId))
        self.db.commit()

    def setUserInterests(self, interests: List[Tuple[int, int]]):
        with self.db.cursor(pymysql.cursors.DictCursor) as db:
            db.executemany(addUserInterestSQL, interests)
        self.db.commit()

    def getUserInterests(self, wdfId):
        with self.db.cursor(pymysql.cursors.DictCursor) as db:
            db.execute(getUserInterestsSQL % (wdfId))
            return db.fetchall()

    def getUserTags(self, wdfId):
        with self.db.cursor(pymysql.cursors.DictCursor) as db:
            db.execute(getUserTagsSQL % (wdfId))
            return db.fetchall()

    def setTag(self, wdfId, interestId, word):
        with self.db.cursor(pymysql.cursors.DictCursor) as db:
            db.execute(setUserTagSQL, (wdfId, interestId, word))
        self.db.commit()

    def callUpdateDf(self, url, word):
        with self.db.cursor(pymysql.cursors.DictCursor) as db:
            db.execute('CALL update_df(%s, %s)', (url, word))
        self.db.commit()

    def computeBestWords(self):
        with self.db.cursor() as db:
            db.execute(computeBestWordsSQL)
        self.db.commit()

    # Trackers
    def getMostPresentTrackers(self, wdfId):
        getMostPresentTrackersSQL = """SELECT requestDomain, COUNT(urlDomain) AS count FROM `pagerequests` WHERE wdfId = %s AND `urlDomain` != `requestDomain` GROUP BY requestDomain ORDER BY count DESC LIMIT 100"""
        with self.db.cursor() as db:
            db.execute(getMostPresentTrackersSQL % wdfId)
            return db.fetchall()

    def getMostRevealingDomains(self, wdfId):
        getMostRevealingDomainsSQL = """SELECT urlDomain, COUNT(requestDomain) AS count FROM `pagerequests` WHERE wdfId = %s AND `urlDomain` != `requestDomain` GROUP BY urlDomain ORDER BY count DESC LIMIT 100"""
        with self.db.cursor() as db:
            db.execute(getMostRevealingDomainsSQL % wdfId)
            return db.fetchall()

    def getTrackers(self, wdfId):
        getTrackersSQL = """SELECT * FROM `precalc_trackers` WHERE wdfId = %s AND `urlDomain` != `reqDomain`"""
        with self.db.cursor() as db:
            db.execute(getTrackersSQL % wdfId)
            return db.fetchall()

    def getTrackersNb(self, wdfId):
        getTrackersNbSQL = """SELECT COUNT(DISTINCT requestDomain) AS count FROM `pagerequests` WHERE wdfId = %s"""
        with self.db.cursor() as db:
            db.execute(getTrackersNbSQL % wdfId)
        return db.fetchone()

    # General stats

    def getGeneralStats(self):
        getTrackersNbSQL = """SELECT COUNT(DISTINCT requestDomain) AS trackersNb, COUNT(requestDomain) AS totalRequests FROM `pagerequests`"""
        with self.db.cursor() as db:
            db.execute(getTrackersNbSQL)
        return db.fetchone()

    def __timeCondition(self, fromArg, toArg):
        result = ""
        if fromArg is not None:
            result += " AND `timestamp` >= '" + fromArg + " 00:00:00' "
        if toArg is not None:
            result += " AND `timestamp` <= '" + toArg + " 23:59:59' "
        return result