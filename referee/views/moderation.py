from flask import Blueprint, g, current_app, session, redirect, request, render_template, flash
from requests_oauthlib import OAuth2Session

from referee.models.user import User
from referee.models.game import Game
from referee.util.auth import Auth
from referee.db import emit
from referee import STARTED
import humanize
from datetime import datetime

moderation = Blueprint('moderation', __name__, url_prefix='/moderation')

@moderation.route('/')
@Auth.mod
def moderation_main():
    stats = {}
    stats['users'] = len(User.select())
    stats['uptime'] = humanize.naturaldelta(datetime.utcnow() - STARTED)
    stats['games'] = len(Game.select())
    x = 0
    for g in Game.select():
        x = x + len(g.attendees)
    stats['attendees'] = x
    games = Game.select()
    return render_template('moderation.html', stats=stats, games=games)

@moderation.route('/games')
@Auth.mod
def moderation_games():
    games = Game.select()
    return render_template('games.html', games=games)

@moderation.route('/game/<gid>', methods=['GET', 'POST'])
@Auth.mod
def moderation_game_edit(gid):
    game = Game.select().where(Game.id == gid).limit(1).get()
    if request.method == 'POST':
        flash('{} was updated successfully!'.format(game.name), 'success')
        game.update_from_form(request.form)
        emit('GAME_UPDATE', game=game.name)
        return redirect('moderation/games')
    return render_template('game.html', game=game)