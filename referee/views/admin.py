from flask import Blueprint, g, current_app, session, redirect, request, render_template
from requests_oauthlib import OAuth2Session

from referee.models.user import User
from referee.util.auth import Auth

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.route('/')
@Auth.admin
def admin_main():
    return render_template('admin.html')