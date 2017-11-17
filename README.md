# wdf-server

**wdf-server** is the server part of the "Web Digital Footprints and Data Privacy" project from [SDIPI](https://sdipi.ch).

## Prerequisites

This project requires at least [Python](https://www.python.org) 3.6.0 installed and a running [MySQL](https://www.mysql.com) instance.

## Installing

Admitting you invoke python using `python3.6`, install the required dependencies listed in `requirements.txt` using pip :

```
python3.6 -m pip install -r requirements.txt
```

You'll also need to set some parameters :

- Rename the **file** `config.ini.example` to `config.ini` and fill in the informations to connect to your MySQL database.
- Set the Facebook App ID the **variable** [`OAUTH2_CLIENT_ID` in server.py](server.py#L20).
- Set the Facebook App Secret in an **environment variable** named `COLLECTSERVER_FACEBOOKSECRET`.

<!-- No tests yet : This will be useful later

## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```
-->

## Deployment

Simply run `server.py` :

```
python 3.6 server.py
```