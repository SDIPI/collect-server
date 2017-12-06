#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This file is part of wdf-server.
"""
from argparse import ArgumentParser
from configparser import ConfigParser, NoOptionError

import gensim
from gensim import corpora


class LDAWDF:
    def __init__(self, mysql):
        self.mysql = mysql

    def trainFromStart(self):
        with self.mysql as db:
            content = db.getContentsText()
        q_in = []
        for item in content:
            q_in.append(item['content'].split())

        dictionary = corpora.Dictionary(q_in)

        doc_term_matrix = [dictionary.doc2bow(doc) for doc in q_in]

        # Running and Trainign LDA model on the document term matrix.
        self.ldamodel = gensim.models.ldamodel.LdaModel(doc_term_matrix, num_topics=10, id2word=dictionary, passes=50)

    def printTest(self):
        print(self.ldamodel.print_topics(num_topics=10, num_words=8))

    def get_document_topics(self, document):
        return self.ldamodel.get_document_topics(document)

if __name__ == '__main__':
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
    config.read('config.ini')

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

    mysql = mysqlConnection()

    wdf = LDAWDF(mysql)
    wdf.trainFromStart()
    wdf.printTest()