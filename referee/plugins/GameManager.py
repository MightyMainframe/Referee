"""Manages all game related bits"""
from datetime import datetime, timedelta

import gevent
from disco.bot import Plugin
from disco.types.channel import (ChannelType, PermissionOverwrite,
                                 PermissionOverwriteType)
from disco.util.snowflake import to_snowflake

from referee.constants import (EMOJIS, GAME_ADD_STEPS, GAME_INFO_STEPS,
                               REACTIONS_MESSAGE, TEAM_CATEGORY, CommandLevel)
from referee.models.game import ExecMode, ExecType, Game
from referee.util.input import parse_duration
from referee.util.timing import Eventual


class GameManager(Plugin):
    """Manages all game related bits"""
    def load(self, ctx):
        super(GameManager, self).load(ctx)
        self.trigger_task = Eventual(self.trigger_schedule)
        self.spawn_later(10, self.queue_triggers)

    def queue_triggers(self):
        try:
            next_trigger = Game.select().order_by(
                (Game.next_announcement).asc()
            ).where(Game.next_announcement != None).limit(1).get()
        except Game.DoesNotExist:
            return

        self.trigger_task.set_next_schedule(next_trigger.next_announcement)

    def trigger_schedule(self):
        games = Game.select().where(
            Game.next_announcement < (datetime.utcnow() + timedelta(seconds=1))
        )
        for game in games:
            message = game.a_message
            channel = self.state.channels.get(game.a_channel)
            if not channel:
                self.log.warning('Not triggering announcement, channel %s was not found!',
                                 game.a_channel)
            channel.send_message(message)
            game.set_interval(game.interval)
        self.queue_triggers()


    def add_game(self, event, name, desc, create_channels=False):
        """
        Sets up a new game
        """
        if create_channels:
            channel_name = name.replace(' ', '-')
            guild = event.msg.guild
            category = guild.create_category(channel_name)
            a_channel = category.create_text_channel('announcements')
            a_channel.topic = desc

        Game.new(name=name, desc=desc, ac=a_channel.id if create_channels else None)

    def join_team(self, name, user):
        team_channels = []
        channels = self.bot.client.state.channels
        for channel in channels:
            channel = self.bot.client.state.channels.get(channel)
            if channel.guild and channel.parent:
                if channel.parent.id == TEAM_CATEGORY and channel.type == ChannelType.guild_voice:
                    team_channels.append(channel)
        teams = {}
        for channel in team_channels:
            c_name = channel.name.lower()
            t_name = c_name.replace(' team', '')
            teams[t_name] = channel
        if name not in teams.keys():
            team_names = ''
            for team_name in teams:
                team_names += '{}\n'.format(team_name)
            return 'Non existant team! Choose from: ```{}```'.format(team_names)

        PermissionOverwrite.create_for_channel(teams[name], user, allow=36701184)
        return 'Added {} to team {}'.format(user.mention, name)

    @Plugin.command('team', '<name:str>', level=CommandLevel.DEV)
    def team_command(self, event, name):
        name = name.replace('_', ' ').lower()
        event.msg.reply(self.join_team(name, event.msg.author))

    @Plugin.listen('MessageReactionAdd', conditional=lambda e:
                   e.message_id == REACTIONS_MESSAGE and e.emoji.id in EMOJIS)
    def on_reaction_add(self, event):
        if event.user_id == self.bot.client.state.me.id:
            return
        if 'team' in event.emoji.name.lower():
            team = event.emoji.name.lower().replace('mmteam', '')
            reply = self.join_team(team, event.guild.members[event.user_id].user)
        else:
            game_name = EMOJIS[event.emoji.id].replace('MM', '')
            game = Game.get_game_by_name(game_name) # type: Game
            if not game:
                reply = 'Game {} not found, check your spelling and try again'.format(game_name)
            else:
                reply = game.execute(event, mode=ExecMode.reaction)
        event.guild.members[event.user_id].user.open_dm().send_message(reply)
        event.delete()

    @Plugin.command('clear', group='teams', level=CommandLevel.MOD)
    def clear_command(self, event):
        team_channels = []
        channels = self.bot.client.state.channels
        for channel in channels:
            channel = self.bot.client.state.channels.get(channel)
            if channel.guild and channel.parent:
                if channel.parent.id == TEAM_CATEGORY:
                    team_channels.append(channel)
        for channel in team_channels:
            for overwrite in channel.overwrites.values():
                if overwrite.type == PermissionOverwriteType.member:
                    overwrite.delete()
        event.msg.reply('Cleared teams!')

    @Plugin.command('start', '<game:str>', level=CommandLevel.MOD)
    def start_command(self, event, game):
        game = game.replace('_', ' ')
        game = Game.get_game_by_name(game)
        if not game:
            return event.msg.reply('Game not found, check your spelling and try again')
        return game.execute(event, exec_type='start')

    @Plugin.command('join', '<game:str>', level=CommandLevel.DEV)
    def join_command(self, event, game):
        game = game.replace('_', ' ')
        game = Game.get_game_by_name(game)
        if not game:
            return event.msg.reply('Game not found, check your spelling and try again')
        return game.execute(event)

    @Plugin.command('set', '<game:str>, <key:str>, <value:str...>', group='g', level=CommandLevel.MOD)
    def set_command(self, event, game, key, value):
        game = game.replace('_', ' ')
        game = Game.get_game_by_name(game)
        if not game:
            return event.msg.reply('Game not found, check your spelling and try again')
        if key == 'a_m' or key == 'a_message':
            query = Game.update(a_message=value)
        elif key == 'a_c' or key == 'a_channel':
            query = Game.update(a_channel=value)
        elif key == 'alias':
            if ' ' in value:
                return event.msg.reply('Alias can\'t contain spaces!')
            query = Game.update(alias=value)
        elif key == 'role':
            try:
                role = to_snowflake(value)
            except:
                return
            else:
                query = Game.update(join_role=role)
        else:
            return event.msg.reply('Invalid key, check your spelling and try again')
        query.where(Game.name == game.name).execute()
        return event.msg.reply('Okay! Set value {} for key {} on {}'.format(value, key, game.name))

    @Plugin.command('set', '<src_type:str>, <game:str>', group='code', level=-1)
    def code_set_command(self, event, src_type, game):
        game = game.replace('_', ' ')
        game = Game.get_game_by_name(game) # type: Game
        src = event.codeblock
        if src_type == 'join':
            game.set_exec_code(src)
            event.msg.reply('Okay! Set ```{}``` as join code for {}'.format(src, game.name))
        elif src_type == 'start':
            game.set_exec_code(src, exec_type=ExecType.start)
            event.msg.reply('Okay! Set ```{}``` as start code for {}'.format(src, game.name))
        else:
            event.msg.reply('Either `!code set join` or `!code set start`')

    @Plugin.command('schedule', '<game:str>, <interval:str>', group='game', level=-1)
    def schedule_command(self, event, game, interval):
        game = Game.get_game_by_name(game)
        if not game:
            event.msg.reply('Game not found, check your spelling and try again')
            return
        if interval == 'clear':
            game.clear_interval()
            event.msg.reply('Cleared interval for {}'.format(game.name))
            self.queue_triggers()
            return
        if not game.a_channel or not game.a_message:
            event.msg.reply('Please be sure to set an announcement message and channel first!')
            return
        game.set_interval(interval)
        event.msg.reply('Okay! Set interval {} for {}'.format(interval, game.name))
        self.queue_triggers()

    @Plugin.command('add', group='game', level=-1)
    def add_command(self, event):
        """Gets all info required for creating a new game"""
        messages_to_delete = []

        def remove_messages():
            """If process is canceled, remove all messages marked for deletion"""
            for message in messages_to_delete:
                message.delete()

        msg = event.msg
        confirm_msg = msg.reply(GAME_ADD_STEPS['validate'])
        messages_to_delete.append(msg)
        messages_to_delete.append(confirm_msg)
        try:
            messages_to_delete.append(self.wait_for_event(
                'MessageCreate',
                conditional=lambda e: (
                    e.message.content.lower().startswith('y') and e.message.author == msg.author
                )
            ).get(timeout=30))
        except gevent.Timeout:
            messages_to_delete.append(msg.reply(GAME_ADD_STEPS['fail']))
            remove_messages()
            return
        for key, value in GAME_INFO_STEPS.iteritems():
            messages_to_delete.append(msg.reply(value))
            try:
                message = self.wait_for_event(
                    'MessageCreate',
                    conditional=lambda e: (
                        e.message.author == msg.author
                    )
                ).get(timeout=30)
            except gevent.Timeout:
                messages_to_delete.append(msg.reply(GAME_ADD_STEPS['fail']))
                remove_messages()
                return
            if key == 'get_name':
                game_name = message.content
            elif key == 'get_desc':
                game_desc = message.content
            else:
                create_channels = bool(message.content.lower().startswith('y'))
        msg.reply('{}'.format(
            GAME_ADD_STEPS['complete'].format(
                game_name, game_desc, ('' if create_channels is True else ' not')
            )
        ))
        self.add_game(event, game_name, game_desc, create_channels)
