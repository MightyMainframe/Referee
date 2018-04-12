from flask import Blueprint, g, current_app, session, redirect, request, render_template, flash
from requests_oauthlib import OAuth2Session

from referee.models.user import User
from referee.models.game import Game
from referee.util.auth import Auth
from referee.db import emit

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.route('/')
@Auth.admin
def admin_main():
    games = Game.select()
    return render_template('admin.html', games=games)

@admin.route('/game/<gid>', methods=['GET', 'POST'])
@Auth.admin
def moderation_game_edit(gid):
    game = Game.select().where(Game.id == gid).limit(1).get()
    if request.method == 'POST':
        flash('{} was updated successfully!'.format(game.name), 'success')
        game.update_from_form(request.form)
        emit('GAME_UPDATE', game=game.name)
        return redirect('admin/games')
    return render_template('admin_game.html', game=game)