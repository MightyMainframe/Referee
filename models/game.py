from peewee import (BigIntegerField, BooleanField, CharField, IntegerField,
                    SmallIntegerField, TextField)

from db import BaseModel


@BaseModel.register
class Game(BaseModel):
    """Game Object"""
    game_id = IntegerField(primary_key=True)
    name = CharField()
    desc = TextField()
    a_channel = BigIntegerField(null=True)

    class Meta:
        db_table = 'games'

    def set_announcement_channel(self, a_channel):
        query = Game.update(a_channel=a_channel)
        query.where(Game.game_id == self.game_id).execute()

    @classmethod
    def new(cls, name, desc):
        return cls.create(
            name=name,
            desc=desc
        )

    @classmethod
    def get_game_by_name(cls, name):
        try:
            return Game.select().where(
                Game.name == name
            ).limit(1).get()
        except Game.DoesNotExist:
            return None
