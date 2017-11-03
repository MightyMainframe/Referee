from datetime import datetime

from peewee import (BigIntegerField, BooleanField, CharField, DateTimeField,
                    IntegerField, SmallIntegerField, TextField)

from referee.db import BaseModel
from referee.util.input import parse_duration


@BaseModel.register
class Game(BaseModel):
    """Game Object"""
    name = CharField()
    desc = TextField()
    a_channel = BigIntegerField(null=True)
    interval = DateTimeField(null=True)
    last_announcement = DateTimeField()

    class Meta:
        db_table = 'games'

    def set_announcement_channel(self, a_channel):
        query = Game.update(a_channel=a_channel)
        query.where(Game.game_id == self.game_id).execute()

    def set_interval(self, interval):
        print 'Heck'
        interval = parse_duration(interval)
        print interval

    @classmethod
    def new(cls, name, desc, ac=None):
        return cls.create(
            name=name,
            desc=desc,
            a_channel=ac,
            interval=None,
            last_announcement=datetime.utcnow()
        )

    @classmethod
    def get_game_by_name(cls, name):
        try:
            return Game.select().where(
                Game.name == name
            ).limit(1).get()
        except Game.DoesNotExist:
            return None
