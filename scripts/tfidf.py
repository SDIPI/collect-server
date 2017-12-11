#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This file is part of wdf-server.
"""
import threading
from argparse import ArgumentParser
from configparser import ConfigParser, NoOptionError
from queue import Queue
from math import log

from mysql import MySQL

# Argument parsing
parser = ArgumentParser(
    description="launches the computation of the tf-idf for the database.")
parser.add_argument("-v", "--verbose", help="be verbose", action="store_true")
parser.add_argument("-n", "--hostname", help="Database address")
parser.add_argument("-u", "--user", help="Database user name")
parser.add_argument("-w", "--password", help="Database's user password")
parser.add_argument("-d", "--name", help="Database's name")

args = parser.parse_args()

# Config file parsing
config = ConfigParser()
config.read('../config.ini')

try:
    server_ip = config.get('server', 'listen')
except NoOptionError:
    server_ip = None

if args.hostname:
    db_host = args.hostname
else:
    db_host = config.get('database', 'host')

if args.user:
    db_user = args.user
else:
    db_user = config.get('database', 'user')

if args.password:
    db_pass = args.password
else:
    db_pass = config.get('database', 'password')

if args.password:
    db_name = args.name
else:
    db_name = config.get('database', 'name')

def mysqlConnection() -> MySQL:
    return MySQL(db_host, db_user, db_pass, db_name)

class wdf_worker(threading.Thread):
    """
    A worker that computes some HTML pages
    """
    def __init__(self, q_in: Queue, id, q_out: {}):
        threading.Thread.__init__(self)
        self.q_out = q_out
        self.id    = id
        self.name  = "wdf_worker_"+str(id)
        self.q_in  = q_in

    def computeDocument(self, text):
        """
        Computes the TF of an document's content
        :param text: Cleaned text of a page.
        :return: 
        """
        tf = {}
        tokens = text.split()
        for token in tokens:
            if token in tf:
                tf[token] += 1
            else:
                tf[token] = 1

        return tf

    # Runs the thread
    def run(self):
        running = True
        while running:
            content = self.q_in.get()
            if content is None:
                break
            tf = self.computeDocument(content['content'])
            self.q_out[content['url']] = tf
            self.q_in.task_done()

q_in = Queue()
tfs = {}

print("Connecting to database")

mysql = mysqlConnection()
with mysql as db:
    content = db.getContentsText()

for item in content:
    q_in.put(item)

for i in range(3):
    t = wdf_worker(q_in, i, tfs)
    t.start()

print("Computing TF : Workers started...")

q_in.join()

for i in range(3):
    q_in.put(None)

df = {}

print("Computing DF...")

for url in tfs:
    terms = tfs[url]
    for word in terms:
        if word in df:
            df[word] += 1
        else :
            df[word] = 1

documents = len(tfs)

tfidfs = {}

print("Computing TF-IDF...")

for url in tfs:
    terms = tfs[url]
    tfidfs[url] = {}
    for word in terms:
        tfidfs[url][word] = terms[word] * log(documents / df[word])

with mysql as db:
    print("Emptying computed tables...")
    db.emptyTfDf()
    print("Setting TFs...")
    db.setTf(tfs)
    print("Setting DFs...")
    db.setDf(df)
    print("Setting TF-IDFs...")
    db.setTfIdf(tfidfs)
    print("Keeping best 20 words for each url...")
    db.computeBestWords()
print("Done.")