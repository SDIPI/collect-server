#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This file is part of wdf-server.
"""
import os
from threading import Thread

from functools import wraps

import math
from langdetect import detect

import lxml.html
from lxml.html.clean import Cleaner

from stop_words import get_stop_words

import requests
import secrets
import re
from flask import Flask, render_template, request, session, redirect, abort, current_app, Response, jsonify
from flask_cors import CORS
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import MissingCodeError

from lda import LDAWDF
from utils import clean_html

from mysql import MySQL

DEBUG = True

OAUTH2_CLIENT_ID = '1921967898054907'
OAUTH2_CLIENT_SECRET = os.environ['COLLECTSERVER_FACEBOOKSECRET']
OAUTH2_SCOPE = ['public_profile']
API_BASE_URL = 'https://graph.facebook.com/v2.10'
OAUTH2_REDIRECT_URI = 'http://df.sdipi.ch:5000/auth'

AUTHORIZATION_URL = 'https://www.facebook.com/v2.10/dialog/oauth'
TOKEN_URL = API_BASE_URL + '/oauth/access_token'

if 'http://' in OAUTH2_REDIRECT_URI:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


def token_updater(token):
    session['oauth2_token'] = token


import re
datePattern = re.compile("^\d{1,4}-\d{1,2}-\d{1,2}$")


def apiMethod(method):
    @wraps(method)
    def withCORS(*args, **kwds):
        response = method(*args, **kwds)
        origin = request.environ['HTTP_ORIGIN'] if ('HTTP_ORIGIN' in request.environ) else "*"
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
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


def facebook_session(token=None, state=None):
    return OAuth2Session(
        client_id=OAUTH2_CLIENT_ID,
        token=token,
        state=state,
        scope=OAUTH2_SCOPE,
        redirect_uri=OAUTH2_REDIRECT_URI,
        auto_refresh_kwargs={
            'client_id': OAUTH2_CLIENT_ID,
            'client_secret': OAUTH2_CLIENT_SECRET
        },
        auto_refresh_url=TOKEN_URL,
        token_updater=token_updater)


app = Flask(__name__)
CORS(app)
app.debug = True
app.config['SECRET_KEY'] = OAUTH2_CLIENT_SECRET
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False


def getHTML(url: str, wdfId: str, connection: MySQL):
    with connection as db:
        lastDay = db.getLastDayContents(url)
    if lastDay:
        return
    if ("http://" in url or "https://" in url) and (url[:17] != "http://localhost:" and url[:17] != "http://localhost/"):
        # Detect if content is even HTML
        customHeaders = {
            'User-Agent': 'server:ch.sdipi.wdf:v3.1.0 (by /u/protectator)',
        }
        contentHead = requests.head(url, headers=customHeaders)
        if 'html' not in contentHead.headers['content-type']:
            return

        htmlContent = requests.get(url, headers=customHeaders)
        with connection as db:
            htmlParsed = lxml.html.fromstring(htmlContent.text)
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
            bestText = clean_html(htmlContent.text, stop_words, (lang == 'en'))
            db.content(wdfId, url, htmlContent.text, lang, title)
            db.setContentText(url, bestText, title, lang)


def mysqlConnection() -> MySQL:
    return MySQL(current_app.config['DB_HOST'], current_app.config['DB_USER'], current_app.config['DB_PASS'],
                 current_app.config['DB_NAME'])


def idOfToken(token):
    if token is None:
        return None
    wdfId = None
    for wdfId in users:
        if users[wdfId]['wdfToken'] == token:
            break
    return wdfId


def tfIdf(tf, df, documents):
    return tf * math.log(documents / df)


users = {}
lda: LDAWDF = None


@app.before_first_request
def first():
    global users, lda
    mysql = mysqlConnection()
    lda = LDAWDF(mysql)
    with mysql as db:
        allUsers = db.getUsers()
        users = {}
        for user in allUsers:
            users[user['wdfId']] = user
    if lda.canLoad():
        print("Loading local LDA Model...")
        lda.load()
    else:
        print("No LDA Model found. Learning from DB...")
        lda.trainFromStart()
        print("Saving the model.")
        lda.save()


##########
# Routes #


@app.route("/")  # Index
def root():
    return render_template("layout.html", contentTemplate="index.html")


@app.route("/facebookauth")  # Redirection to Facebook authorization page
def facebookauth():
    facebook = facebook_session()
    authorization_url, state = facebook.authorization_url(AUTHORIZATION_URL)
    session['oauth2_state'] = state
    return redirect(authorization_url)


@app.route("/auth")  # Redirect from Facebook auth
def auth():
    if request.values.get('error'):
        return request.values['error']
    # Get facebook token + user infos
    try:
        facebook = facebook_session(state=session.get('oauth2_state'))
        token = facebook.fetch_token(
            TOKEN_URL,
            client_secret=OAUTH2_CLIENT_SECRET,
            authorization_response=request.url.strip())
        user = facebook.get(API_BASE_URL + '/me').json()
        # Save infos in db
        wdf_token = secrets.token_hex(32)
        with mysqlConnection() as db:
            db.newOrUpdateUser(user['id'], token['access_token'], wdf_token)

        response = redirect('/authsuccess?code=' + wdf_token)
        response.set_cookie('wdfToken', wdf_token, 60 * 60 * 24 * 365 * 10, domain=".sdipi.ch")
        return response

    except MissingCodeError:
        return render_template("layout.html", warningMessage="Missing code.")


@app.route("/authsuccess")  # Redirect from Facebook auth
def authsuccess():
    global users
    if request.values.get('error'):
        return request.values['error']
    facebook = facebook_session(state=session.get('oauth2_state'))
    # user = facebook.get(API_BASE_URL + '/me').json()
    mysql = mysqlConnection()
    with mysql as db:
        allUsers = db.getUsers()
        users = {}
        for user in allUsers:
            users[user['wdfId']] = user

    return render_template("layout.html", contentTemplate="loginsuccess.html", userName='user', userId='id')


@app.route("/collect", methods=['POST'])  # Call from script
@apiMethod
def collect():
    if request.values.get('error'):
        return request.values['error']

    data = request.get_json()
    mysql = mysqlConnection()
    wdfId = idOfToken(data['accessToken'])
    if wdfId is None:
        resp = jsonify({'error': "Not connected"})
        return resp
    with mysql as db:
        db.pageView(wdfId, data['url'])

    # Thread
    thread = Thread(target=getHTML, args=(data['url'], wdfId, mysql))
    thread.start()

    resp = Response('{"result":"ok"}')

    return resp


@app.route("/collectRequest", methods=['POST'])  # Call from script
@apiMethod
def collectRequest():
    if request.values.get('error'):
        return request.values['error']

    data = request.get_json()
    mysql = mysqlConnection()
    wdfId = idOfToken(data['accessToken'])
    if wdfId is None:
        resp = jsonify({'error': "Not connected"})
        return resp
    with mysql as db:
        db.pageRequest(wdfId, data['url'], data['request'], data['method'])

    resp = Response('{"result":"ok"}')

    return resp


@app.route("/collectEvent", methods=['POST'])  # Call from script
@apiMethod
def collectEvent():
    if request.values.get('error'):
        return request.values['error']

    data = request.get_json()
    mysql = mysqlConnection()
    wdfId = idOfToken(data['accessToken'])
    if wdfId is None:
        resp = jsonify({'error': "Not connected"})
        return resp
    with mysql as db:
        db.pageEvent(wdfId, data['url'], data['type'], data['value'])

    resp = Response('{"result":"ok"}')

    return resp


@app.route("/collectWatch", methods=['POST'])  # Call from script
@apiMethod
def collectWatch():
    if request.values.get('error'):
        return request.values['error']

    data = request.get_json()
    mysql = mysqlConnection()
    wdfId = idOfToken(data['accessToken'])
    if wdfId is None:
        resp = jsonify({'error': "Not connected"})
        return resp
    with mysql as db:
        db.watchEvents(wdfId, data['value'])

    resp = Response('{"result":"ok"}')

    return resp

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
        mostVisited = db.getMostWatchedSites(wdfId, fromArg, toArg)
    return jsonify(mostVisited)


@app.route("/api/tfIdfSites", methods=['GET'])  # Call from interface
@userConnected
@apiMethod
def tfIdfSites(wdfId):
    mysql = mysqlConnection()
    with mysql as db:
        tfIdf = db.getTfIdfForUser(wdfId)
    return jsonify(tfIdf)


@app.route("/api/interests", methods=['GET'])  # Call from interface
@userConnected
@apiMethod
def interests(wdfId):
    mysql = mysqlConnection()
    with mysql as db:
        tfIdfData = db.getTfIdfForUser(wdfId)
        nb = db.getNbDocuments()['count']
        w = {}
        wList = []
        for word in tfIdfData:
            if word['word']in w:
                w[word['word']] += tfIdf(word['tf'], word['df'], nb)
            else:
                w[word['word']] = tfIdf(word['tf'], word['df'], nb)
        for el in w:
            wList.append({'word': el, 'weight': w[el]})

        wList.sort(key=lambda x: x['weight'], reverse=True)
        wWords = [el['word'] for el in wList]
        topics = lda.get_terms_topics(wWords)
    return jsonify(topics)


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


def run(ip, port, db_host, db_user, db_pass, db_name):
    app.config['DB_HOST'] = db_host
    app.config['DB_USER'] = db_user
    app.config['DB_PASS'] = db_pass
    app.config['DB_NAME'] = db_name

    connection = MySQL(db_host, db_user, db_pass, db_name)
    with connection as test:
        pass

    app.run(host=ip, port=port, threaded=True)
