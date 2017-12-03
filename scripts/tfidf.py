#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This file is part of wdf-server.
"""
import threading
import re
from argparse import ArgumentParser
from configparser import ConfigParser, NoOptionError
from queue import Queue
import nltk
from nltk.stem import WordNetLemmatizer

from stop_words import get_stop_words

import lxml.html
from lxml.html.clean import Cleaner

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

stop_words = get_stop_words('en') + get_stop_words('fr')

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

    def computePage(self, raw_html, lang):
        """
        Computes the TF of an HTML page's content and updates the IDF
        :param html: HTML of a page.
        :return: 
        """

        # Parse the HTML
        htmlContent = lxml.html.fromstring(raw_html)

        cleaner = Cleaner()
        cleaner.javascript = True
        cleaner.style = True

        text = cleaner.clean_html(htmlContent).text_content()

        pattern = re.compile(r'[^\W\d_]+', re.U)
        words = nltk.word_tokenize(text)

        tf = {}

        try:
            stop_words = get_stop_words(lang)
        except:
            stop_words = []

        if lang == 'en':
            lemmatiser = WordNetLemmatizer()
            wordnet_tag ={'NN':'n','JJ':'a','VB':'v','RB':'r'}
            tagged = nltk.pos_tag(words)
            for token in tagged:
                word = token[0].lower()
                if pattern.match(word) is not None:
                    if word not in stop_words:
                        try:
                            lemma = lemmatiser.lemmatize(word, wordnet_tag[token[1][:2]])
                        except:
                            lemma = lemmatiser.lemmatize(word)
                        if lemma in tf:
                            tf[lemma] += 1
                        else:
                            tf[lemma] = 1

        else:
            for word in words:
                word = word.lower()
                if pattern.match(word) is not None:
                    if word not in stop_words:
                        if word in tf:
                            tf[word] += 1
                        else:
                            tf[word] = 1

        return tf

    # Runs the thread
    def run(self):
        running = True
        while running:
            content = self.q_in.get()
            if content is None:
                break
            tf = self.computePage(content['content'], content['language'])
            self.q_out[content['url']] = tf
            self.q_in.task_done()

q_in = Queue()
tfs = {}

mysql = mysqlConnection()
with mysql as db:
    content = db.getContents()

for item in content:
    q_in.put(item)

for i in range(3):
    t = wdf_worker(q_in, i, tfs)
    t.start()

q_in.join()

for i in range(3):
    q_in.put(None)

df = {}

for url in tfs:
    terms = tfs[url]
    for word in terms:
        if word in df:
            df[word] += 1
        else :
            df[word] = 1

with mysql as db:
    db.emptyTfDf()
    db.setTf(tfs)
    db.setDf(df)