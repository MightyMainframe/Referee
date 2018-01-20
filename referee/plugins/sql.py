import time
import gevent
import psycopg2
import pygal
import cairosvg

from gevent.pool import Pool
from holster.enum import Enum
from holster.emitter import Priority
from datetime import datetime

from disco.types.base import UNSET
from disco.types.message import MessageTable
from disco.types.user import User as DiscoUser
from disco.types.channel import Channel as DiscoChannel, MessageIterator
from disco.util.snowflake import to_datetime, from_datetime
from disco.bot import Plugin

from referee.db import database
from referee.models.user import User
from referee.util.input import parse_duration


class SQLPlugin(Plugin):
    global_plugin = True

    def load(self, ctx):
        self.models = ctx.get('models', {})
        self.backfills = {}
        super(SQLPlugin, self).load(ctx)

    def unload(self, ctx):
        ctx['models'] = self.models
        super(SQLPlugin, self).unload(ctx)
    
    @Plugin.listen('PresenceUpdate')
    def on_presence_update(self, event):
        updates = {}

        if event.user.avatar != UNSET:
            updates['avatar'] = event.user.avatar
        
        if event.user.username != UNSET:
            updates['username'] = event.user.username

        if event.user.discriminator != UNSET:
            updates['discriminator'] = int(event.user.discriminator)
        
        if not updates:
            return

        User.update(**updates).where((User.user_id == event.user.id)).execute()

    @Plugin.listen('MessageCreate')
    def on_message_create(self, event):
        User.from_disco_user(event.message.author)
        for user in event.message.mentions.values():
            User.from_disco_user(user)

    @Plugin.listen('GuildCreate')
    def on_guild_create(self, event):
        for member in list(event.members.values()):
            User.from_disco_user(member.user)

    @Plugin.listen('GuildMemberAdd')
    def on_guild_member_add(self, event):
        User.from_disco_user(event.member.user)