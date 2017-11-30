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
contentSQL = 'INSERT INTO `content` (wdfId, url, timestamp, `content`) VALUES (%s, %s, CURRENT_TIMESTAMP, %s)'

# Collect Server SQL
getUsersSQL = 'SELECT * FROM `users`'
getContentsSQL = 'SELECT * FROM `content`'
getLastDayContentsSQL = 'SELECT `id`, `wdfId`, `url`, `timestamp` FROM `content` WHERE url LIKE CONCAT(\'%s\', \'%%\') AND timestamp >= DATE_ADD(NOW(), INTERVAL -1 DAY)'

newuserSQL = 'INSERT INTO users (wdfId, facebookAccessToken, wdfToken) VALUES ("%s", "%s", "%s")'
newOrUpdateuserSQL = "INSERT INTO users (facebookId, facebookAccessToken, wdfToken) VALUES (%(fbId)s, %(fbToken)s, %(wdfToken)s) ON DUPLICATE KEY UPDATE facebookId = %(fbId)s, facebookAccessToken = %(fbToken)s, wdfToken = %(wdfToken)s"

# Compute SQL
emptyTfTableSQL = "TRUNCATE computed_tf"
emptyDfTableSQL = "TRUNCATE computed_df"
emptyWatchTableSQL = "TRUNCATE computed_watch"

getUserVisibilitySQL = "SELECT * FROM `event` WHERE `wdfId` = %s AND `type` LIKE 'visibility' ORDER BY `timestamp` ASC"

tfSQL = 'INSERT IGNORE INTO `computed_tf` (url, word, tf) VALUES (%s, %s, %s)'
dfSQL = 'INSERT IGNORE INTO `computed_df` (word, df) VALUES (%s, %s)'
watchSQL = 'INSERT IGNORE INTO `computed_watch` (wdfId, url, time) VALUES (%s, %s, %s)'

# Interface SQL
mostVisitedSitesSQL = 'SELECT url, COUNT(*) AS count FROM `pageviews` WHERE `wdfId`=%s GROUP BY `url`'
mostWatchedSitesSQL = 'SELECT url, time FROM `computed_watch` WHERE `wdfId`=%s'

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

    def content(self, wdfId, url, content):
        with self.db.cursor() as db:
            db.execute(contentSQL, (wdfId, url, content))
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
            users = db.fetchall()
        return users

    def getContents(self):
        with self.db.cursor(pymysql.cursors.DictCursor) as db:
            db.execute(getContentsSQL)
            contents = db.fetchall()
        return contents

    def getLastDayContents(self, url):
        with self.db.cursor(pymysql.cursors.DictCursor) as db:
            db.execute(getLastDayContentsSQL % (url))
            contents = db.fetchall()
        return contents

    def getVisibilityEventsByUser(self):
        events = {}
        with self.db.cursor(pymysql.cursors.DictCursor) as db:
            db.execute(getUsersSQL)
            users = db.fetchall()
            for user in users:
                db.execute(getUserVisibilitySQL, (user['wdfId']))
                events[user['wdfId']] = db.fetchall()
        return events

    def emptyTfDf(self):
        with self.db.cursor() as db:
            db.execute(emptyTfTableSQL)
            db.execute(emptyDfTableSQL)
        self.db.commit()

    def emptyWatch(self):
        with self.db.cursor() as db:
            db.execute(emptyWatchTableSQL)
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

    def setWatch(self, watchs):
        with self.db.cursor() as db:
            db.executemany(watchSQL, watchs)
        self.db.commit()

    def getMostVisitedSites(self, wdfId):
        with self.db.cursor(pymysql.cursors.DictCursor) as db:
            db.execute(mostVisitedSitesSQL, (wdfId))
            mostVisitedSites = db.fetchall()
        return mostVisitedSites

    def getMostWatchedSites(self, wdfId):
        with self.db.cursor(pymysql.cursors.DictCursor) as db:
            db.execute(mostWatchedSitesSQL, (wdfId))
            mostWatchedSites = db.fetchall()
        return mostWatchedSites

    def getTfIdfForUrl(self, url):
        with self.db.cursor(pymysql.cursors.DictCursor) as db:
            db.execute(tfIdfForUrlSQL, (url))
            tfIdf = db.fetchall()
        return tfIdf

    def getTfIdfForUser(self, wdfId):
        with self.db.cursor(pymysql.cursors.DictCursor) as db:
            db.execute(tfDfForUserSQL, (wdfId))
            tfIdf = db.fetchall()
        return tfIdf

    def getNbDocuments(self):
        with self.db.cursor(pymysql.cursors.DictCursor) as db:
            db.execute(nbDocumentsSQL)
            nb = db.fetchone()
        return nb
