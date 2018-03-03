from flask import g, redirect
from httplib import FORBIDDEN
from referee.models.user import User
from referee.constants import get_user_level, check_global_admin
import gevent

import functools

members = {}

class Auth:
    @staticmethod
    def admin(func=None):
        if callable(func):
            return _authed(func, -1)
        else:
            return functools.partial(_authed)

    @staticmethod
    def mod(func=None):
        if callable(func):
            return _authed(func, 2)
        else:
            return functools.partial(_authed)

    @staticmethod
    def default(func=None):
        if callable(func):
            return _authed(func, 0)
        else:
            return functools.partial(_authed)

def _authed(func, level):
    @functools.wraps(func)
    def deco(*args, **kwargs):
        if not hasattr(g, 'user') or g.user == None:
            return redirect('/login')
        user = g.user # type: User
        if check_global_admin(user.user_id) or level == 0:
            return func(*args, **kwargs)
        if level == -1:
            return redirect('/')
        if level == 2 and not user.moderator:
            return redirect('/')
        return func(*args, **kwargs)
    return deco
