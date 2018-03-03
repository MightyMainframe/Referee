from peewee import (BigIntegerField, BooleanField, CharField, IntegerField,
                    NaiveQueryResultWrapper, SmallIntegerField, TextField, DateTimeField)
from datetime import datetime
from referee.db import BaseModel
from referee.constants import GLOBAL_ADMINS


@BaseModel.register
class User(BaseModel):
    """User class for storing user data"""
    user_id = BigIntegerField(primary_key=True, unique=True)
    username = TextField()
    discriminator = SmallIntegerField()
    avatar = TextField(null=True)
    bot = BooleanField(default=False)
    mc_name = CharField(default='')
    mc_uuid = CharField(default='')
    steam_name = CharField(default='')
    battle_tag = CharField(default='')
    points = IntegerField(default=0)

    created_at = DateTimeField(default=datetime.utcnow)

    moderator = BooleanField(default=False)

    metadata_fields = ['blizzard', 'minecraft', 'steam']

    SQL = '''
        CREATE INDEX IF NOT EXISTS users_username_trgm ON users USING gin(username gin_trgm_ops);
    '''

    class Meta:
        db_table = 'users'

        indexes = (
            (('user_id', 'username', 'discriminator'), True),
        )

    @classmethod
    def get_metadata_fields(cls):
        return ', '.join(cls.metadata_fields)

    
    @classmethod
    def from_disco_user(cls, user, should_update=True):
        obj, _ = cls.get_or_create(
            user_id=user.id,
            defaults={
                'username': user.username,
                'discriminator': user.discriminator,
                'avatar': user.avatar,
                'bot': user.bot
            })

        if should_update:
            updates = {}

            if obj.username != user.username:
                updates['username'] = user.username

            if obj.discriminator != user.discriminator:
                updates['discriminator'] = user.discriminator

            if obj.avatar != user.avatar and user.avatar:
                updates['avatar'] = user.avatar

            if updates:
                cls.update(**updates).where(User.user_id == user.id).execute()

        return obj

    @classmethod
    def with_id(cls, uid):
        try:
            return User.get(user_id=uid)
        except User.DoesNotExist:
            return None

    @property
    def admin(self):
        return self.user_id in GLOBAL_ADMINS

    @property
    def id(self):
        return self.user_id

    @property
    def avatar_url(self):
        return self.get_avatar_url()

    def get_avatar_url(self, fmt='png', size=1024):
        if not self.avatar:
            return 'https://cdn.discordapp.com/embed/avatars/0.png'

        return 'https://cdn.discordapp.com/avatars/{}/{}.{}?size={}'.format(
            self.user_id,
            self.avatar,
            fmt,
            size
        )

    def get_metadata(self):
        return 'Minecraft name: {}, Steam: {}, Battle Tag: {}'.format(
            self.mc_name if self.mc_name else 'None', 
            self.steam_name if self.steam_name else 'None',
            self.battle_tag if self.battle_tag else 'None'
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
