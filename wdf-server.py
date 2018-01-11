#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This file is part of wdf-server.
"""
from argparse import ArgumentParser
from configparser import ConfigParser, NoOptionError
import server


# Argument parsing
parser = ArgumentParser(
    description="starts the wdf-server server for SDIPI's Web Digital Footprints project.")
parser.add_argument("-v", "--verbose", help="be verbose", action="store_true")
parser.add_argument("-n", "--hostname", help="Database address")
parser.add_argument("-u", "--user", help="Database user name")
parser.add_argument("-w", "--password", help="Database's user password")
parser.add_argument("-d", "--name", help="Database's name")
parser.add_argument("-p", "--port", help="Port number to listen to")
parser.add_argument("-l", "--lda", help="Subfolder from which to load LDA model")

args = parser.parse_args()

# Config file parsing
config = ConfigParser()
config.read('config.ini')

try:
    server_ip = config.get('server', 'listen')
except NoOptionError:
    server_ip = None

if args.port:
    server_port = args.port
else:
    server_port = config.getint('server', 'port')

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

if args.lda:
    lda = args.lda
else:
    lda = None

server.run(ip=server_ip, port=server_port, db_host=db_host, db_user=db_user, db_pass=db_pass, db_name=db_name, lda=lda)