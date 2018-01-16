"""
This file is part of wdf-server.
"""
import threading
from argparse import ArgumentParser
from configparser import ConfigParser, NoOptionError
from queue import Queue
from math import log
import pymysql as pymysql
from urllib.parse import urlparse

import math

from mysql import MySQL

# Argument parsing
parser = ArgumentParser(
    description="pre-computes the trackers per user.")
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

selectSQL = "SELECT wdfId, urlDomain, requestDomain, COUNT(size) as 'amount', SUM(size) as 'size' FROM `pagerequests` GROUP BY `wdfId`,`urlDomain`,`requestDomain`"
updateSQL = "INSERT INTO `precalc_trackers` (wdfId, urlDomain, reqDomain, amount, size) VALUES (%(id)s, %(url)s, %(request)s, %(amount)s, %(size)s) ON DUPLICATE KEY UPDATE amount = %(amount)s, size = %(size)s"

mysql = mysqlConnection()
print("Grouping requests...")
with mysql as db:
    with db.db.cursor(pymysql.cursors.DictCursor) as cur:
        cur.execute(selectSQL)
        requests = cur.fetchall()

domains = []
domainsDict = {}
print("Preparing update...")
for req in requests:
    url = req['urlDomain']
    request = req['requestDomain']
    wdfId = str(req['wdfId'])
    amount = str(req['amount'])
    size = str(int(req['size']))
    domains.append({'id': wdfId, 'url': url, 'request': request, 'amount': amount, 'size': size})

print("Updating...")
with mysql as db:
    with db.db.cursor(pymysql.cursors.DictCursor) as cur:
        for domain in domains:
            cur.execute(updateSQL, domain)
    db.db.commit()

print("Done.")