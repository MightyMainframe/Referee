import json
import subprocess

from flask import (Blueprint, flash, g, make_response, redirect,
                   render_template, request, url_for)

from referee.models.user import User
from referee.plugins.UserManager import get_mc_uuid, check_regex
from referee.util.auth import Auth
from referee.constants import BATTLE_TAG, MC_NAME, STEAM_NAME, MC_UUID

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
            tag = BATTLE_TAG.search(battle_tag)
            if not check_regex(tag):
                flash('Invalid battle tag', 'error')
                return redirect(url_for('dash.metadata'))
            tag = tag.string
            user.add_battle_tag(tag)
        if mc_name != user.mc_name and mc_name != None:
            name = MC_NAME.search(mc_name)
            if not check_regex(name):
                flash('Invalid minecraft name provided', 'error')
                return redirect(url_for('dash.metadata'))
            name = name.string
            uuid = get_mc_uuid(name)
            check = MC_UUID.search(uuid)
            if not check_regex(check):
                flash('Invalid minecraft name provided', 'error')
                return redirect(url_for('dash.metadata'))
            uuid = check.string
            uuid = uuid[:8]+"-"+uuid[8:12]+"-"+uuid[12:16]+"-"+uuid[16:20]+"-"+uuid[20:]
            user.add_minecraft_data(name, uuid)
        if steam_name != user.steam_name and steam_name != None:
            name = STEAM_NAME.search(steam_name)
            if not check_regex(name):
                flash('Invalid steam name provided', 'error')
                return redirect(url_for('dash.metadata'))
            name = name.string
            user.add_steam_name(name)
        flash('Metadata updated!')
        return redirect(url_for('dash.metadata'))

    return render_template('metadata.html')

@dashboard.route('/login')
def dash_login():
    return render_template('login.html')
