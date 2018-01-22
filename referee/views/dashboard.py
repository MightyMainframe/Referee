import json
import subprocess

from flask import (Blueprint, flash, g, make_response, redirect,
                   render_template, request)

from referee.models.user import User
from referee.plugins.UserManager import get_mc_uuid
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
        mc_name = request.form['minecraft']
        steam_name = request.form['steam']
        user = g.user # type: User
        if battle_tag != user.battle_tag and battle_tag != None:
            user.add_battle_tag(battle_tag)
        if mc_name != user.mc_name and mc_name != None:
            user.add_minecraft_data(mc_name, get_mc_uuid(mc_name))
        if steam_name != user.steam_name and steam_name != None:
            user.add_steam_name(steam_name)
        print('Metadata updated!')
        flash('Metadata updated!')
        return redirect('/')

    return render_template('metadata.html')

@dashboard.route('/login')
def dash_login():
    return render_template('login.html')
