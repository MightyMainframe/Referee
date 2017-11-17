"""Manages all game related bits"""
import gevent
from disco.bot import Plugin
from disco.util.snowflake import to_snowflake
from disco.types.channel import PermissionOverwrite, PermissionOverwriteType, ChannelType

from datetime import datetime, timedelta

from referee.constants import GAME_ADD_STEPS, GAME_INFO_STEPS, check_global_admin, TEAM_CATEGORY
from referee.models.game import Game
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

    @Plugin.command('clear', group='teams', level=-1)
    def clear_command(self, event):
        team_channels = []
        channels = self.bot.client.state.channels
        for channel in channels:
            channel = self.bot.client.state.channels.get(channel)
            if channel.parent:
                if channel.parent.id == TEAM_CATEGORY:
                    team_channels.append(channel)
        for channel in team_channels:
            for overwrite in channel.overwrites.values():
                if overwrite.type == PermissionOverwriteType.member:
                    overwrite.delete()
        event.msg.reply('Cleared teams!')


    @Plugin.command('team', '<name:str>', level=-1)
    def team_command(self, event, name):
        name = name.replace('_', ' ').lower()
        team_channels = []
        channels = self.bot.client.state.channels
        for channel in channels:
            channel = self.bot.client.state.channels.get(channel)
            if channel.parent:
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
            return event.msg.reply('Non existant team! Choose from: ```{}```'.format(team_names))

        PermissionOverwrite.create_for_channel(teams[name], event.msg.author, allow=36701184)
        return event.msg.reply('Added {} to team {}'.format(event.msg.author.mention, name))


    @Plugin.command('join', '<game:str>', level=-1)
    def join_command(self, event, game):
        game = game.replace('_', ' ')
        game = Game.get_game_by_name(game)
        if not game:
            return event.msg.reply('Game not found, check your spelling and try again')
        return game.execute_join(event)

    @Plugin.command('set', '<game:str>, <key:str>, <value:str...>', group='g', level=-1)
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
