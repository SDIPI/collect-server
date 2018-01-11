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
    description="fills the domains in the pagerequests table.")
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

selectSQL = "SELECT * FROM `pagerequests`"
updateSQL = "UPDATE `pagerequests` SET urlDomain = %s, requestDomain = %s WHERE id=%s"

mysql = mysqlConnection()
with mysql as db:
    with db.db.cursor(pymysql.cursors.DictCursor) as cur:
        cur.execute(selectSQL)
        pagerequests = cur.fetchall()

domains = []
for req in pagerequests:
    urlDomain = urlparse(req['url']).netloc
    reqDomain = urlparse(req['request']).netloc
    id = req['id']
    domains.append((urlDomain, reqDomain, id))
    if id%10000 == 0:
        print(id)

print("Updating...")
with mysql as db:
    with db.db.cursor(pymysql.cursors.DictCursor) as cur:
        cur.executemany(updateSQL, domains)
    db.db.commit()

print("Done.")