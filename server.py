#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This file is part of wdf-server.
"""
import math
import subprocess
import re
import json
from functools import wraps
from threading import Thread

import lxml.html
import requests
import secrets
from flask import Flask, render_template, request, redirect, abort, current_app, Response, jsonify
from configparser import ConfigParser, NoOptionError
from flask_compress import Compress
from flask_cors import CORS
from langdetect import detect
from lxml.html.clean import Cleaner
from oauthlib.oauth2 import MissingCodeError
from stop_words import get_stop_words
from urllib.parse import urlparse

from lda import LDAWDF
from mysql import MySQL
from utils import clean_html

DEBUG = True

datePattern = re.compile("^\d{1,4}-\d{1,2}-\d{1,2}$")

filteredSitesParser = ConfigParser()
filteredSitesParser.read('ignorelist.ini')
patterns = json.loads(filteredSitesParser.get('ignore_regex', 'patterns'))


def apiMethod(method):
    @wraps(method)
    def withCORS(*args, **kwds):
        response = method(*args, **kwds)
        origin = request.environ['HTTP_ORIGIN'] if ('HTTP_ORIGIN' in request.environ) else "*"
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = "true"
        return response

    return withCORS


def userConnected(method):
    @wraps(method)
    def with_userConnected(*args, **kwds):
        wdfToken = request.cookies.get('wdfToken')
        wdfId = idOfToken(wdfToken)
        if wdfId is None:
            return jsonify({'error': "Not connected"})
        return method(wdfId, *args, **kwds)

    return with_userConnected


app = Flask(__name__)
Compress(app)
CORS(app)
app.debug = True
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False


@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers['Access-Control-Allow-Credentials'] = "true"
    return r


def getHTML(url: str, wdfId: str, connection: MySQL):
    with connection as db:
        lastDay = db.getLastDayContents(url)
    if lastDay:
        return
    if ("http://" in url or "https://" in url) and (
            url[:17] != "http://localhost:" and url[:17] != "http://localhost/"):

        # Detect if content is even HTML
        customHeaders = {
            'User-Agent': 'server:ch.sdipi.wdf:v3.1.0 (by /u/protectator)',
        }
        try:
            contentHead = requests.head(url, headers=customHeaders)
        except requests.exceptions.SSLError as e:
            print("SSL Exception while getHTML of " + url)
            print(e)
            return
        if 'content-type' in contentHead.headers:
            if 'html' not in contentHead.headers['content-type']:
                return

        chrome_process = subprocess.run(["node", "./js/index.js", url], stdout=subprocess.PIPE)

        if chrome_process.returncode == 0:
            htmlContentRaw = chrome_process.stdout.decode('utf8')

            htmlContent = re.sub("<", " <", htmlContentRaw)
            with connection as db:

                htmlParsed = lxml.html.fromstring(htmlContent)
                try:
                    title = htmlParsed.find(".//title").text
                except:
                    title = ""

                cleaner = Cleaner()
                cleaner.javascript = True
                cleaner.style = True
                textClean = cleaner.clean_html(htmlParsed).text_content()

                lang = detect(textClean)
                try:
                    stop_words = get_stop_words(lang)
                except:
                    stop_words = []
                bestText = clean_html(htmlContent, stop_words, (lang == 'en'))
                db.content(wdfId, url, htmlContent, lang, title)
                db.setContentText(url, bestText, title, lang)
        else:
            print(chrome_process.stdout)


def mysqlConnection() -> MySQL:
    return MySQL(current_app.config['DB_HOST'], current_app.config['DB_USER'], current_app.config['DB_PASS'],
                 current_app.config['DB_NAME'])


def idOfToken(token):
    if token is None:
        return None
    for wdfId in users:
        if users[wdfId]['wdfToken'] == token:
            return wdfId
    return None


def tfIdf(tf, df, documents):
    return tf * math.log(documents / df)


users = {}
lda: LDAWDF = None
bestWords: {} = None


@app.before_first_request
def first():
    global users, lda, bestWords
    mysql = mysqlConnection()
    lda = LDAWDF(mysql)
    users = {}
    bestWords = {}
    with mysql as db:
        allUsers = db.getUsers()
        for user in allUsers:
            users[user['wdfId']] = user
        bestWordsList = db.getBestWords()
    for entry in bestWordsList:
        url = entry['url']
        if url not in bestWords:
            bestWords[url] = []
        bestWords[url].append({'word': entry['word'], 'tfidf': entry['tfidf']})
    if app.config['LDA_SUBFOLDER']:
        print("Loading local LDA Model from " + app.config['LDA_SUBFOLDER'])
        lda.load(app.config['LDA_SUBFOLDER'])
    elif lda.canLoad():
        print("Loading local LDA Model...")
        lda.load()
    else:
        print("No LDA Model found. Learning from DB...")
        try:
            lda.trainFromStart()
            print("Saving the model.")
            lda.save()
        except ValueError:
            print('Seemingly fresh installation. Not computing LDA.')


##########
# Routes #


@app.route("/")  # Index
def root():
    return render_template("layout.html", contentTemplate="index.html")


@app.route("/anonauth") # Create a new anonymous account
def anonauth():
    if request.values.get('error'):
        return request.values['error']
    # Get facebook token + user infos
    try:
        # Save infos in db
        wdf_token = secrets.token_hex(32)
        with mysqlConnection() as db:
            db.newAnonUser(wdf_token)

        response = redirect('/authsuccess?code=' + wdf_token)
        response.set_cookie('wdfToken', wdf_token, 60 * 60 * 24 * 365 * 10, domain=".sdipi.ch")
        return response

    except MissingCodeError:
        return render_template("layout.html", warningMessage="Missing code.")


@app.route("/reconnect", methods=['POST']) # Sets the cookie as asked
def reconnect():
    if request.values.get('error'):
        return request.values['error']
    try:
        data = request.get_json()
        token = data['accessToken']
        wdfId = idOfToken(data['accessToken'])
        if wdfId is None:
            resp = jsonify({'error': "Not connected"})
            return resp

        response = jsonify({'success': "Connected", "wdfId": wdfId})
        response.set_cookie('wdfToken', token, 60 * 60 * 24 * 365 * 10, domain=".sdipi.ch")
        return response

    except MissingCodeError:
        return render_template("layout.html", warningMessage="Missing code.")


@app.route("/disconnect") # Sets the cookie as asked
@userConnected
def disconnect(wdfId):
    if request.values.get('error'):
        return request.values['error']
    try:
        if wdfId is None:
            resp = jsonify({'error': "Not connected"})
            return resp

        response = jsonify({'success': "Disconnected"})
        response.set_cookie('wdfToken', '', 0, domain=".sdipi.ch")
        return response

    except MissingCodeError:
        return render_template("layout.html", warningMessage="Missing code.")


@app.route("/authsuccess")  # Redirect from Facebook auth
def authsuccess():
    global users
    if request.values.get('error'):
        return request.values['error']
    mysql = mysqlConnection()
    with mysql as db:
        allUsers = db.getUsers()
        users = {}
        for user in allUsers:
            users[user['wdfId']] = user

    return render_template("layout.html", contentTemplate="loginsuccess.html", userName='user', userId='id')


@app.route("/collectActions", methods=['POST'])  # Call from extension
@apiMethod
def collectActions():
    if request.values.get('error'):
        return request.values['error']

    data = request.get_json()
    wdfId = idOfToken(data['accessToken'])
    if wdfId is None:
        resp = jsonify({'error': "Not connected"})
        return resp

    for action in data['value']:
        actionData = action['data']
        actionType = action['type']
        if actionType == 'request':
            treatRequest(wdfId, actionData)
        elif actionType == 'watch':
            treatWatch(wdfId, actionData)
        elif actionType == 'view':
            treatView(wdfId, actionData)
        elif actionType == 'event':
            continue

    resp = Response('{"result":"ok"}')

    return resp

def treatRequest(wdfId, data):
    mysql = mysqlConnection()
    urlDomain = urlparse(data['url']).netloc
    reqDomain = urlparse(data['request']).netloc
    with mysql as db:
        db.pageRequest(wdfId, data['url'], data['request'], data['method'], data['size'], urlDomain, reqDomain)

def treatWatch(wdfId, data):
    # Removing filtered sites
    filtered = {}
    for site in data:
        if not isFilteredSite(site):
            filtered[site] = data[site]

    mysql = mysqlConnection()
    with mysql as db:
        db.watchEvents(wdfId, filtered)

def treatView(wdfId, data):
    if isFilteredSite(data['url']):
        return
    mysql = mysqlConnection()
    with mysql as db:
        db.pageView(wdfId, data['url'])
    thread = Thread(target=getHTML, args=(data['url'], wdfId, mysql))
    thread.name = "Thread_getHTML_" + data['url']
    thread.start()

#
# /api/
#

@app.route("/api/connectionState", methods=['GET'])  # Call from interface
@userConnected
@apiMethod
def connectionState(wdfId):
    return jsonify({'success': "Connected", "wdfId": wdfId})


@app.route("/api/mostVisitedSites", methods=['GET'])  # Call from interface
@userConnected
@apiMethod
def mostVisitedSites(wdfId):
    fromArg = request.args.get('from')
    toArg = request.args.get('to')
    if fromArg and not datePattern.match(fromArg):
        return jsonify({'error': "Incorrect parameter from"})
    if toArg and not datePattern.match(toArg):
        return jsonify({'error': "Incorrect parameter to"})
    mysql = mysqlConnection()
    with mysql as db:
        mostVisited = db.getMostVisitedSites(wdfId, fromArg, toArg)
    for site in mostVisited:
        site['words'] = bestWords[site['url']] if site['url'] in bestWords else []
    return jsonify(mostVisited)


@app.route("/api/mostWatchedSites", methods=['GET'])  # Call from interface
@userConnected
@apiMethod
def mostWatchedSites(wdfId):
    fromArg = request.args.get('from')
    toArg = request.args.get('to')
    if fromArg and not datePattern.match(fromArg):
        return jsonify({'error': "Incorrect parameter from"})
    if toArg and not datePattern.match(toArg):
        return jsonify({'error': "Incorrect parameter to"})
    mysql = mysqlConnection()
    with mysql as db:
        mostWatched = db.getMostWatchedAndTopics(wdfId, fromArg, toArg)[:200]
    for site in mostWatched:
        site['words'] = bestWords[site['url']] if site['url'] in bestWords else []
    return jsonify(mostWatched)


@app.route("/api/allTopics", methods=['GET'])  # Call from interface
@userConnected
@apiMethod
def allTopics(wdfId):
    mysql = mysqlConnection()
    with mysql as db:
        terms = db.getLdaTopics()
    return jsonify(terms)


@app.route("/api/historySites", methods=['GET'])  # Call from interface
@userConnected
@apiMethod
def historySites(wdfId):
    fromArg = request.args.get('from')
    toArg = request.args.get('to')
    if fromArg and not datePattern.match(fromArg):
        return jsonify({'error': "Incorrect parameter from"})
    if toArg and not datePattern.match(toArg):
        return jsonify({'error': "Incorrect parameter to"})
    mysql = mysqlConnection()
    with mysql as db:
        history = db.getHistorySites(wdfId, fromArg, toArg)
    return jsonify(history)


@app.route("/api/oldestEntry", methods=['GET'])  # Call from interface
@userConnected
@apiMethod
def oldestEntry(wdfId):
    mysql = mysqlConnection()
    with mysql as db:
        oldest = db.getOldestEntry(wdfId)
    return jsonify(oldest)


@app.route("/api/nbDocuments", methods=['GET'])  # Call from interface
@apiMethod
def nbDocuments():
    mysql = mysqlConnection()
    with mysql as db:
        nb = db.getNbDocuments()
    return jsonify(nb)


@app.route("/api/interestsList", methods=['GET'])  # Call from interface
@userConnected
@apiMethod
def interestsList(wdfId):
    mysql = mysqlConnection()
    with mysql as db:
        oldest = db.getInterestsList()
    return jsonify(oldest)


@app.route("/api/setInterests", methods=['GET'])  # Call from interface
@userConnected
@apiMethod
def setInterests(wdfId):
    interests = request.args.get('data').split(',')
    result = []
    for interest in interests:
        result.append((wdfId, interest))
    mysql = mysqlConnection()
    with mysql as db:
        db.cleanUserInterests(wdfId)
        interests = db.setUserInterests(result)
    return jsonify(interests)


@app.route("/api/getInterests", methods=['GET'])  # Call from interface
@userConnected
@apiMethod
def getInterests(wdfId):
    mysql = mysqlConnection()
    with mysql as db:
        userInterests = db.getUserInterests(wdfId)
    return jsonify(userInterests)


@app.route("/api/setTag", methods=['GET'])  # Call from interface
@userConnected
@apiMethod
def setTag(wdfId):
    interestId = request.args.get('interestId')
    topicId = request.args.get('topicId')
    words = request.args.get('words')
    mysql = mysqlConnection()
    with mysql as db:
        db.setTag(wdfId, interestId, words)
        db.setCurrentTag(wdfId, interestId, topicId)
    resp = {'result': "ok"}
    return jsonify(resp)


@app.route("/api/getTags", methods=['GET'])  # Call from interface
@userConnected
@apiMethod
def getTags(wdfId):
    mysql = mysqlConnection()
    with mysql as db:
        userTags = db.getUserTags(wdfId)
    return jsonify(userTags)


@app.route("/api/getCurrentTags", methods=['GET'])  # Call from interface
@userConnected
@apiMethod
def getCurrentTags(wdfId):
    mysql = mysqlConnection()
    with mysql as db:
        userTags = db.getUserCurrentTags(wdfId)
    return jsonify(userTags)


@app.route("/api/getUrlsTopic", methods=['GET'])  # Call from interface
@userConnected
@apiMethod
def getUrlsTopic(wdfId):
    mysql = mysqlConnection()
    with mysql as db:
        userInterests = db.getUrlsTopic()
    return jsonify(userInterests)


# Trackers

@app.route("/api/getTrackers", methods=['GET'])  # Call from interface
@userConnected
@apiMethod
def getTrackers(wdfId):
    mysql = mysqlConnection()
    with mysql as db:
        trackers = db.getTrackers(wdfId)
    return jsonify(trackers)

@app.route("/api/getTrackersStats", methods=['GET'])  # Call from interface
@userConnected
@apiMethod
def getTrackersStats(wdfId):
    mysql = mysqlConnection()
    with mysql as db:
        trackers = db.getTrackersNb(wdfId)
    resp = {'nbTrackers': trackers['count']}
    return jsonify(resp)

# General stats

@app.route("/api/getGeneralStats", methods=['GET'])  # Call from interface
@userConnected
@apiMethod
def getGeneralStats(wdfId):
    mysql = mysqlConnection()
    with mysql as db:
        stats = db.getGeneralStats()
    return jsonify(stats)


@app.errorhandler(401)
def unauthorized(e):
    return render_template("layout.html", content="Error 401", warningMessage=e.description), 401


@app.errorhandler(403)
def forbidden(e):
    return render_template("layout.html", content="Error 403"), 403


@app.errorhandler(404)
def page_not_found(e):
    return render_template("layout.html", content="Error 404"), 404


@app.errorhandler(412)
def page_not_found(e):
    return render_template("layout.html", content="Error 412", warningMessage=e.description), 412


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("layout.html", content="Error 500"), 500


@app.context_processor
def utility_processor():
    def serverimg(server, hash):
        if hash:
            return 'https://cdn.discordapp.com/icons/' + server + '/' + hash + '.png'
        else:
            return '/static/discord_logo.png'

    return dict(serverimg=serverimg)


def check_auth(user):
    if user is None:
        abort(401, "Missing user")


def isFilteredSite(url):
    for pattern in patterns:
        m = re.match(pattern, url)
        if m:
            return True
    return False


def run(ip, port, db_host, db_user, db_pass, db_name, lda):
    app.config['DB_HOST'] = db_host
    app.config['DB_USER'] = db_user
    app.config['DB_PASS'] = db_pass
    app.config['DB_NAME'] = db_name
    app.config['LDA_SUBFOLDER'] = lda

    connection = MySQL(db_host, db_user, db_pass, db_name)
    with connection as test:
        pass

    app.run(host=ip, port=port, threaded=True)


# Config file parsing
config = ConfigParser()
config.read('/home/ubuntu/collect-server/config.ini')

db_host = config.get('database', 'host')
db_user = config.get('database', 'user')
db_pass = config.get('database', 'password')
db_name = config.get('database', 'name')

app.config['DB_HOST'] = db_host
app.config['DB_USER'] = db_user
app.config['DB_PASS'] = db_pass
app.config['DB_NAME'] = db_name
app.config['LDA_SUBFOLDER'] = 'backup8'

connection = MySQL(db_host, db_user, db_pass, db_name)
with connection as test:
    pass