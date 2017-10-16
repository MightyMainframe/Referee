from peewee import (BigIntegerField, SmallIntegerField, CharField, TextField, BooleanField, IntegerField)
from db import BaseModel

@BaseModel.register
class Game(BaseModel):
    """Game Object"""
    name = CharField()
    desc = TextField()

    class Meta:
        db_table = 'games'

    @classmethod
    def new(self, name, desc):
        return self.create(
            name=name,
            desc=desc
        )
