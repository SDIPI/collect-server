#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This file is part of wdf-server.
"""
from argparse import ArgumentParser
from configparser import ConfigParser, NoOptionError
from pathlib import Path
from mysql import MySQL
import gensim
import mysql
from gensim import corpora
from gensim.models.ldamodel import LdaModel
from gensim.models.callbacks import PerplexityMetric


class LDAWDF:
    mysql: mysql.MySQL
    ldamodel: LdaModel
    dictionary = None
    corpus = None

    def __init__(self, mysql):
        self.mysql = mysql
        self.dataFolder = './data/'
        self.saveFile = 'lda_model'
        self.saveFileDict = 'lda_model_dict'

    def trainFromStart(self):
        with self.mysql as db:
            content = db.getContentsText()
        documents = []
        for item in content:
            documents.append(item['content'].split())

        self.dictionary = corpora.Dictionary(documents)

        self.dictionary.filter_extremes(no_below=5, no_above=0.5)

        doc_term_matrix = [self.dictionary.doc2bow(doc) for doc in documents]

        self.corpus = doc_term_matrix

        # Running and Training LDA model on the document term matrix.
        print("Starting to train LDA Model...")
        self.ldamodel = LdaModel(
            doc_term_matrix,
            num_topics=200,
            id2word=self.dictionary,
            passes=100)

    def printTest(self):
        print(self.ldamodel.print_topics(num_topics=10, num_words=5))

    def save(self):
        self.ldamodel.save(self.dataFolder + self.saveFile)
        self.dictionary.save(self.dataFolder + self.saveFileDict)

    def canLoad(self):
        my_file = Path(self.dataFolder + self.saveFile)
        my_file_dict = Path(self.dataFolder + self.saveFileDict)
        return my_file.is_file() and my_file_dict.is_file()

    def update(self, corpus):
        self.ldamodel.update(corpus)

    def load(self, subfolder=None):
        if subfolder:
            sf = subfolder + '/'
        else:
            sf = ''
        self.ldamodel = LdaModel.load(self.dataFolder + sf + self.saveFile)
        self.dictionary = gensim.corpora.Dictionary.load(self.dataFolder + sf + self.saveFileDict)

    def fillDb(self):
        topics = {}
        result = []
        result2 = []
        nbTopics = self.ldamodel.get_topics().shape[0]
        # "Old"
        for topicId in range(0, nbTopics):
            topicTerms = self.ldamodel.get_topic_terms(topicId, 3)
            topicTerms.sort(key=lambda x: x[1], reverse=True)
            words = []
            for topicTerm in topicTerms:
                words.append(self.dictionary.get(topicTerm[0]))
            topics[topicId] = ' '.join(words)
        with mysql as db:
            contentsText = db.getContentsText()
            for element in contentsText:
                bow = self.dictionary.doc2bow(element['content'].split())
                docTopics = self.ldamodel.get_document_topics(bow, minimum_probability=0.05)
                if len(docTopics) > 0:
                    docTopics.sort(key=lambda x: x[1], reverse=True)
                    result.append((element['url'], topics[docTopics[0][0]]))
                    for docTopic in docTopics:
                        result2.append((element['url'], docTopic[0], str(docTopic[1])))
            db.emptyUrlsTopic()
            db.emptyCurrentUrlsTopic()
            db.emptyCurrentUserTags()
            db.setCurrentUrlsTopic(result2)
            db.setPrecalcTopics()
        # "New"
        terms = []
        for topicId in range(0, nbTopics):
            topicTerms = self.ldamodel.get_topic_terms(topicId, 5)
            topicTerms.sort(key=lambda x: x[1], reverse=True)
            for topicTerm in topicTerms:
                terms.append((topicId, self.dictionary.get(topicTerm[0]), str(topicTerm[1])))
        with mysql as db:
            db.emptyLdaTopics()
            db.setLdaTopics(terms)


    def get_terms_topics(self, keywords):
        bow = self.dictionary.doc2bow(keywords[:30])
        topics = {}
        keywordsResult = {}
        for word in bow:
            wordTopics = self.ldamodel.get_term_topics(word[0], 0.05)
            keywordsResult[word[0]] = {'word': self.dictionary.get(word[0]), 'topics': wordTopics}
            for wordTopic in wordTopics:
                wordTopicId = wordTopic[0]
                if wordTopicId not in topics:
                    topics[wordTopicId] = self.ldamodel.show_topic(wordTopicId)
        return {'topics': topics, 'keywords': keywordsResult}


if __name__ == '__main__':

    # Argument parsing
    parser = ArgumentParser(
        description="launches the computation of the tf-idf for the database.")
    parser.add_argument("-v", "--verbose", help="be verbose", action="store_true")
    parser.add_argument("-n", "--hostname", help="Database address")
    parser.add_argument("-u", "--user", help="Database user name")
    parser.add_argument("-w", "--password", help="Database's user password")
    parser.add_argument("-d", "--name", help="Database's name")
    parser.add_argument("-t", "--topics", help="Fills the topic for each document in the DB", action="store_true")

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
    if wdf.canLoad():
        wdf.load()
    else:
        print("Training LDA model")
        wdf.trainFromStart()
        print("Saving LDA model")
        wdf.save()
        print("LDA model saved")

    # Fill the DB if asked
    if args.topics:
        print("Filling topics into the DB")
        wdf.fillDb()
        print("DB filled with topics")

    wdf.printTest()

    print("Trying to compute perplexity")
    wdf.ldamodel.bound(wdf.corpus)