from peewee import (BigIntegerField, BooleanField, CharField, IntegerField,
                    NaiveQueryResultWrapper, SmallIntegerField, TextField)

from referee.db import BaseModel


@BaseModel.register
class User(BaseModel):
    """User class for storing user data"""
    user_id = BigIntegerField(primary_key=True, unique=True)
    mc_name = CharField()
    mc_uuid = CharField()
    steam_name = CharField()
    battle_tag = CharField()
    points = IntegerField()

    metadata_fields = ['blizzard', 'minecraft', 'steam']

    @classmethod
    def get_metadata_fields(cls):
        return ', '.join(cls.metadata_fields)

    class Meta:
        db_table = 'users'

    @classmethod
    def get_user_by_id(cls, u_id):
        try:
            user = User.select().where(
                User.user_id == u_id
            ).limit(1).get()
        except User.DoesNotExist:
            raise AttributeError('User not found!')
        return user

    @classmethod
    def new(cls, u_id):
        return cls.create(
            user_id=u_id,
            mc_name='',
            mc_uuid='',
            steam_name='',
            battle_tag='',
            points=0
        )

    def add_points(self, points=0):
        points = points + self.points
        query = User.update(points=points)
        query.where(User.user_id == self.user_id).execute()

    def add_minecraft_data(self, mc_n, uuid):
        query = User.update(mc_name=mc_n, mc_uuid=uuid)
        query.where(User.user_id == self.user_id).execute()

    def add_steam_name(self, s_n):
        query = User.update(steam_name=s_n)
        query.where(User.user_id == self.user_id).execute()

    def add_battle_tag(self, b_tag):
        query = User.update(battle_tag=b_tag)
        query.where(User.user_id == self.user_id).execute()
