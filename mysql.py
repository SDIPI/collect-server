#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This file is part of wdf-server.
"""
import pymysql as pymysql

pageviewSQL = 'INSERT INTO pageviews (wdfId, url, timestamp) VALUES (%s, %s, CURRENT_TIMESTAMP)'
pagerequestSQL = 'INSERT INTO pagerequests (wdfId, url, timestamp, request, method) VALUES (%s, %s, CURRENT_TIMESTAMP, %s, %s)'
pageeventSQL = 'INSERT INTO `event` (wdfId, url, type, `value`) VALUES (%s, %s, %s, %s)'
contentSQL = 'INSERT INTO `content` (wdfId, url, timestamp, `content`) VALUES (%s, %s, CURRENT_TIMESTAMP, %s)'

getUsersSQL = 'SELECT * FROM `users`'
getContentsSQL = 'SELECT * FROM `content`'
getLastDayContentsSQL = 'SELECT `id`, `wdfId`, `url`, `timestamp` FROM `content` WHERE url LIKE CONCAT(%s , '%') AND timestamp >= DATE_ADD(NOW(), INTERVAL -1 DAY)'

newuserSQL = 'INSERT INTO users (wdfId, facebookAccessToken, wdfToken) VALUES ("%s", "%s", "%s")'

newOrUpdateuserSQL = "INSERT INTO users (facebookId, facebookAccessToken, wdfToken) VALUES (%(fbId)s, %(fbToken)s, %(wdfToken)s) ON DUPLICATE KEY UPDATE facebookId = %(fbId)s, facebookAccessToken = %(fbToken)s, wdfToken = %(wdfToken)s"

emptyTfTableSQL = "TRUNCATE computed_tf"
emptyDfTableSQL = "TRUNCATE computed_df"

tfSQL = 'INSERT IGNORE INTO `computed_tf` (url, word, tf) VALUES (%s, %s, %s)'
dfSQL = 'INSERT IGNORE INTO `computed_df` (word, df) VALUES (%s, %s)'

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
        self.db.commit()
        return users

    def getContents(self):
        with self.db.cursor(pymysql.cursors.DictCursor) as db:
            db.execute(getContentsSQL)
            contents = db.fetchall()
        self.db.commit()
        return contents

    def getLastDayContentsSQL(self, url):
        with self.db.cursor(pymysql.cursors.DictCursor) as db:
            db.execute(getLastDayContentsSQL)
            contents = db.fetchall()
        self.db.commit()
        return contents

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