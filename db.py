import redis
from peewee import OP, Expression, Model, Proxy
from playhouse.postgres_ext import PostgresqlExtDatabase

REGISTERED_MODELS = []

database = Proxy()
rdb = redis.Redis()

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


def init_db():
    database.initialize(PostgresqlExtDatabase('referee'))

    for model in REGISTERED_MODELS:
        model.create_table(True)

        if hasattr(model, 'SQL'):
            database.execute_sql(model.SQL)

def reset_db():
    init_db()

    for model in REGISTERED_MODELS:
        model.drop_table(True)
        model.create_table(True)
