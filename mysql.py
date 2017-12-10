#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This file is part of wdf-server.
"""
import pymysql as pymysql

# Collect SQL
pageviewSQL = 'INSERT INTO pageviews (wdfId, url, timestamp) VALUES (%s, %s, CURRENT_TIMESTAMP)'
pagerequestSQL = 'INSERT INTO pagerequests (wdfId, url, timestamp, request, method) VALUES (%s, %s, CURRENT_TIMESTAMP, %s, %s)'
pageeventSQL = 'INSERT INTO `event` (wdfId, url, type, `value`) VALUES (%s, %s, %s, %s)'
contentSQL = 'INSERT INTO `content` (wdfId, url, timestamp, `content`, `language`, `title`) VALUES (%s, %s, CURRENT_TIMESTAMP, %s, %s, %s)'
watcheventSQL = 'INSERT INTO `pagewatch` (wdfId, url, timestamp, amount) VALUES (%s, %s, CURRENT_TIMESTAMP, %s)'
contentTextSQL = 'INSERT IGNORE INTO `content_text` (url, `content`, `title`, `language`) VALUES (%s, %s, %s, %s)'

# Collect Server SQL
getUsersSQL = 'SELECT * FROM `users`'
getContentsSQL = 'SELECT * FROM `content`'
getContentsTextSQL = 'SELECT * FROM `content_text`'
getLastDayContentsSQL = 'SELECT `id`, `wdfId`, `url`, `timestamp` FROM `content` WHERE url LIKE CONCAT(\'%s\', \'%%\') AND timestamp >= DATE_ADD(NOW(), INTERVAL -1 DAY)'

newuserSQL = 'INSERT INTO users (wdfId, facebookAccessToken, wdfToken) VALUES ("%s", "%s", "%s")'
newOrUpdateuserSQL = "INSERT INTO users (facebookId, facebookAccessToken, wdfToken) VALUES (%(fbId)s, %(fbToken)s, %(wdfToken)s) ON DUPLICATE KEY UPDATE facebookId = %(fbId)s, facebookAccessToken = %(fbToken)s, wdfToken = %(wdfToken)s"

# Compute SQL
emptyTfTableSQL = "TRUNCATE computed_tf"
emptyDfTableSQL = "TRUNCATE computed_df"
emptyWatchTableSQL = "TRUNCATE computed_watch"

tfSQL = 'INSERT IGNORE INTO `computed_tf` (url, word, tf) VALUES (%s, %s, %s)'
dfSQL = 'INSERT IGNORE INTO `computed_df` (word, df) VALUES (%s, %s)'

# Interface SQL
mostVisitedSitesSQL = 'SELECT url, COUNT(*) AS count FROM `pageviews` WHERE `wdfId`=%s GROUP BY `url`'
mostWatchedSitesSQL = 'SELECT `wdfId`, `url`, CAST(SUM(`amount`) AS UNSIGNED) AS time FROM `pagewatch` WHERE wdfId=%s GROUP BY wdfId, url ORDER BY SUM(`amount`) DESC'
mostVisitedSitesTemplateSQL1 = 'SELECT url, COUNT(*) AS count FROM `pageviews` WHERE `wdfId`=%s'
mostVisitedSitesTemplateSQL2 = ' GROUP BY `url`'
mostWatchedSitesTemplateSQL1 = 'SELECT `wdfId`, `url`, CAST(SUM(`amount`) AS UNSIGNED) AS time FROM `pagewatch` WHERE wdfId=%s'
mostWatchedSitesTemplateSQL2 = ' GROUP BY wdfId, url ORDER BY SUM(`amount`) DESC'

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

nbDocumentsSQL = "SELECT COUNT(*) AS `count` FROM (SELECT DISTINCT url FROM `computed_tf`) AS `cnt`"

tfIdfForUrlSQL = """SELECT
`computed_tf`.`url` AS `url`,
`computed_tf`.`word` AS `word`,
`computed_tf`.`tf` AS `tf`,
`computed_df`.`df` AS `df`,
`computed_tf`.`tf` * LOG((SELECT COUNT(*) FROM `computed_df`) / `computed_df`.`df`) AS `tfidf`
FROM
`computed_tf`
LEFT JOIN
`computed_df`
ON
`computed_tf`.`word` = `computed_df`.`word`
WHERE
`computed_tf`.`url` = '%s'
ORDER BY `computed_tf`.`tf` DESC"""

tfDfForUserSQL = """
SELECT
`computed_tf`.`url` AS `url`,
`computed_tf`.`word` AS `word`,
`computed_tf`.`tf` AS `tf`,
`computed_df`.`df` AS `df`
FROM
`computed_tf`
LEFT JOIN
`computed_df`
ON
`computed_tf`.`word` = `computed_df`.`word`
WHERE
`computed_tf`.`url` IN (SELECT DISTINCT url FROM `pageviews` WHERE `wdfId`=%s)
ORDER BY `url` DESC, `tf` DESC"""

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

    def pageRequest(self, wdfId, url, request, method):
        with self.db.cursor() as db:
            db.execute(pagerequestSQL, (wdfId, url, request, method))
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

    def getUsers(self):
        with self.db.cursor(pymysql.cursors.DictCursor) as db:
            db.execute(getUsersSQL)
            return db.fetchall()

    def getContents(self):
        with self.db.cursor(pymysql.cursors.DictCursor) as db:
            db.execute(getContentsSQL)
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

    def getTfIdfForUrl(self, url):
        with self.db.cursor(pymysql.cursors.DictCursor) as db:
            db.execute(tfIdfForUrlSQL, (url))
            return db.fetchall()

    def getTfIdfForUser(self, wdfId):
        with self.db.cursor(pymysql.cursors.DictCursor) as db:
            db.execute(tfDfForUserSQL, (wdfId))
            return db.fetchall()

    def getNbDocuments(self):
        with self.db.cursor(pymysql.cursors.DictCursor) as db:
            db.execute(nbDocumentsSQL)
            return db.fetchone()

    def getHistorySites(self, wdfId):
        with self.db.cursor(pymysql.cursors.DictCursor) as db:
            db.execute(historySitesSQL, (wdfId))
            return db.fetchall()

    def getOldestEntry(self, wdfId):
        with self.db.cursor(pymysql.cursors.DictCursor) as db:
            db.execute(oldestEntrySQL, (wdfId))
            return db.fetchone()

    def __timeCondition(self, fromArg, toArg):
        result = ""
        if fromArg is not None:
            result += " AND `timestamp` >= '" + fromArg + " 00:00:00' "
        if toArg is not None:
            result += " AND `timestamp` <= '" + toArg + " 00:00:00' "
        return result