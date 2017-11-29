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

from mysql import MySQL

# Argument parsing
parser = ArgumentParser(
    description="launches the computation of the watch time for the database.")
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
    A worker that computes some wdfID's watch time
    """
    def __init__(self, q_in: Queue, id, q_out: []):
        threading.Thread.__init__(self)
        self.q_out = q_out
        self.id    = id
        self.name  = "wdf_worker_"+str(id)
        self.q_in  = q_in

    def computeWatch(self, events):
        """
        Computes the watch time of an user's URL visibility events
        :param events: Visibility events of an URL
        :return: 
        """

        total = 0
        start = -1

        for event in events:
            if event['value'] == "in":
                start = event['timestamp']
            elif event['value'] == "out":
                if start != -1:
                    total += (event['timestamp'] - start).total_seconds()
                    start = -1
                else:
                    continue

        return total

    # Runs the thread
    def run(self):
        running = True
        while running:
            next = self.q_in.get()
            if next is None:
                break
            wdfId = next[0]
            events = next[1]

            eventsByUrl = {}
            for event in events:
                if event['url'] in eventsByUrl:
                    eventsByUrl[event['url']].append(event)
                else:
                    eventsByUrl[event['url']] = [event]
            for url in eventsByUrl:
                watchTime = self.computeWatch(eventsByUrl[url])
                self.q_out.append((wdfId, url, int(watchTime)))
            self.q_in.task_done()

q_in = Queue()
watchs = []

mysql = mysqlConnection()
with mysql as db:
    users = db.getVisibilityEventsByUser()

for userEvents in users:
    q_in.put((userEvents, users[userEvents]))

for i in range(3):
    t = wdf_worker(q_in, i, watchs)
    t.start()

q_in.join()

for i in range(3):
    q_in.put(None)

with mysql as db:
    db.emptyWatch()
    db.setWatch(watchs)
