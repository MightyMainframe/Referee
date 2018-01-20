from __future__ import absolute_import

import os
import redis
import json

from peewee import OP, Expression, Model, Proxy
from playhouse.postgres_ext import PostgresqlExtDatabase

import psycogreen.gevent; psycogreen.gevent.patch_psycopg()

ENV = os.getenv('ENV', 'local')

if ENV == 'docker':
    rdb = redis.Redis(db=0, host='redis')
else:
    rdb = redis.Redis(db=11)

def emit(typ, **kwargs):
    kwargs['type'] = typ
    rdb.publish('actions', json.dumps(kwargs))

REGISTERED_MODELS = []

database = Proxy()

OP['IRGX'] = 'irgx'


def pg_regex_i(lhs, rhs):
    return Expression(lhs, OP.IRGX, rhs)


PostgresqlExtDatabase.register_ops({OP.IRGX: '~*'})


class BaseModel(Model):
    class Meta:
        database = database

    @staticmethod
    def register(cls):
        REGISTERED_MODELS.append(cls)
        return cls


def init_db(env):
    if env == 'docker':
        database.initialize(PostgresqlExtDatabase(
            'referee',
            host='db',
            user='postgres',
            port=int(os.getenv('PG_PORT', 5432)),
            autorollback=True))
    else:
        database.initialize(PostgresqlExtDatabase(
            'referee',
            user='referee',
            port=int(os.getenv('PG_PORT', 5432)),
            autorollback=True))

    for model in REGISTERED_MODELS:
        model.create_table(True)

        if hasattr(model, 'SQL'):
            database.execute_sql(model.SQL)


def reset_db():
    init_db(ENV)

    for model in REGISTERED_MODELS:
        model.drop_table(True)
        model.create_table(True)
