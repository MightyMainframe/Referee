import json
import subprocess

from flask import Blueprint, render_template, request, g, make_response, redirect

from referee.util.auth import Auth

dashboard = Blueprint('dash', __name__)

@dashboard.route('/')
@Auth.default
def index():
    return render_template('index.html')

@dashboard.route('/metadata', methods=['POST', 'GET'])
@Auth.default
def metadata():
    if request.method == 'POST':
        battle_tag = request.form['blizzard']
        print('Battle tag set to: {}').format(battle_tag)

    return render_template('metadata.html')

@dashboard.route('/login')
def dash_login():
    return render_template('login.html')