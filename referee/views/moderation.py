from flask import Blueprint, g, current_app, session, redirect, request, render_template
from requests_oauthlib import OAuth2Session

from referee.models.user import User
from referee.util.auth import Auth

moderation = Blueprint('moderation', __name__, url_prefix='/moderation')

@moderation.route('/')
@Auth.mod
def moderation_main():
    return render_template('moderation.html')