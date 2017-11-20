import pprint
from datetime import datetime

from holster.enum import Enum
from peewee import (BigIntegerField, BooleanField, CharField, DateTimeField,
                    IntegerField, SmallIntegerField, TextField)
from playhouse.postgres_ext import ArrayField, JSONField

from referee.constants import PY_CODE_BLOCK
from referee.db import BaseModel
from referee.util.input import parse_duration

ExecType = Enum(
    JOIN='join',
    START='start'
)
ExecMode = Enum(
    REACTION='reaction',
    COMMAND='command'
)


@BaseModel.register
class Game(BaseModel):
    """Game Object"""
    name = CharField()
    alias = CharField()
    desc = TextField()
    join_role = BigIntegerField(null=True)
    time_message = BigIntegerField(null=True)
    a_channel = BigIntegerField(null=True)
    a_message = CharField(null=True)
    next_announcement = DateTimeField(null=True)
    last_announcement = DateTimeField()
    interval = CharField(null=True)
    attendees = ArrayField(BigIntegerField)
    join_src = TextField(null=True)
    play_src = TextField(null=True)

    class Meta:
        db_table = 'games'

    def execute(self, event, exec_type=ExecType.join, mode=ExecMode.command):
        ctx = {
            'self': self
        }
        if mode == ExecMode.command:
            ctx['user_id'] = event.msg.author.id
        else:
            ctx['user_id'] = event.user_id

        if exec_type == ExecType.join:
            src = '{}'.format(self.join_src)
        elif exec_type == ExecType.start:
            src = '{}'.format(self.play_src)
        else:
            src = 'event.msg.reply(\'Invalid exec type provided\')'

        if src == '' or src == 'None':
            src = 'event.msg.reply(\'No source provided\')'
        lines = filter(bool, src.split('\n'))
        if lines[-1] and 'return' not in lines[-1]:
            lines[-1] = 'return ' + lines[-1]
        lines = '\n'.join('    ' + i for i in lines)
        code = 'def f():\n{}\nx = f()'.format(lines)
        local = {}
        try:
            exec compile(code, '<eval>', 'exec') in ctx, local
        except Exception as e:
            if mode == ExecMode.command:
                event.msg.reply(PY_CODE_BLOCK.format(type(e).__name__ + ': ' + str(e)))
                return
            else:
                return PY_CODE_BLOCK.format(type(e).__name__ + ': ' + str(e))
        result = pprint.pformat(local['x'])
        if mode == ExecMode.command:
            event.msg.reply(result)
        else:
            return result


    def set_exec_code(self, code, exec_type=ExecType.join):
        if exec_type == ExecType.join:
            query = Game.update(join_src=code)
        elif exec_type == ExecType.start:
            query = Game.update(play_src=code)
        else:
            return
        query.where(Game.name == self.name).execute()

    def set_announcement_channel(self, a_channel):
        query = Game.update(a_channel=a_channel)
        query.where(Game.name == self.name).execute()

    def set_announcement_message(self, message):
        query = Game.update(a_message=message)
        query.where(Game.name == self.name).execute()

    def clear_interval(self):
        query = Game.update(next_announcement=None, interval=None)
        query.where(Game.name == self.name).execute()

    def set_interval(self, interval):
        try:
            next_announcement = parse_duration(interval)
        except:
            print 'Ermahgerd! Something sploded'
            return
        query = Game.update(next_announcement=next_announcement, interval=interval)
        query.where(Game.name == self.name).execute()

    @classmethod
    def new(cls, name, desc, ac=None):
        return cls.create(
            name=name,
            alias=name.replace(' ', '_'),
            desc=desc,
            join_role=None,
            time_message=None,
            a_channel=ac,
            a_message=None,
            interval=None,
            last_announcement=datetime.utcnow(),
            next_announcement=None,
            attendees=[],
            join_src=None,
            play_src=None
        )

    @classmethod
    def get_game_by_name(cls, name):
        try:
            return Game.select().where(
                Game.name == name
            ).limit(1).get()
        except Game.DoesNotExist:
            try:
                return Game.select().where(
                    Game.alias == name
                ).limit(1).get()
            except:
                return None
