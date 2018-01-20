from flask import g, redirect
from httplib import FORBIDDEN
from referee.models.user import User
from referee.constants import get_user_level, check_global_admin

import functools

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
    def dev(func=None):
        if callable(func):
            return _authed(func, 1)
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
        disco_user = __disco_user_from_id(user.user_id)
        if not disco_user:
            return redirect('/')
        if level == -1:
            return redirect('/')
        if level > get_user_level(disco_user):
            return redirect('/')
        return func(*args, **kwargs)
    return deco

def __disco_user_from_id(uid):
    from yaml import load
    from referee.constants import GUILD_ID
    from disco.api.http import Routes, HTTPMethod
    from disco.types.user import User as DiscoUser
    def get_client():
        from disco.client import ClientConfig, Client
        with open('config.yaml', 'r') as f:
            data = load(f)

        config = ClientConfig()
        config.token = data.get('token')
        return Client(config)

    c = get_client()
    u = DiscoUser.create(c.api.client, c.api.http((HTTPMethod.GET, Routes.GUILDS + '/{}/members/{}'.format(GUILD_ID, uid))).json())
    print(u)
    return u
