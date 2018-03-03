import os; os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

import logging

from flask import Flask, g, session
from holster.flask_ext import Holster

from referee import ENV
from referee.db import init_db
from referee.models.user import User

from yaml import load

referee = Holster(Flask(__name__))
logging.getLogger('peewee').setLevel(logging.INFO)

@referee.app.before_first_request
def before_first_request():
    init_db(ENV)

    with open('config.yaml', 'r') as f:
        data = load(f)

    referee.app.config.update(data['web'])
    referee.app.secret_key = data['web']['SECRET_KEY']
    referee.app.config['token'] = data.get('token')


@referee.app.before_request
def check_auth():
    g.user = None
    if 'uid' in session:
        g.user = User.with_id(session['uid'])

@referee.app.after_request
def save_auth(response):
    if g.user and 'uid' not in session:
        session['uid'] = g.user.id
    elif not g.user and 'uid' in session:
        del session['uid']

    return response

@referee.app.context_processor
def inject_data():
    return dict(
        user=g.user,
    )
