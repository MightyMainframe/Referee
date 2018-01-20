"""Core handler for bot"""
import contextlib
import json
import pprint
import time
import traceback
from datetime import datetime

import humanize
import psycopg2
import requests
from disco.bot import Plugin
from disco.bot.command import CommandEvent
from disco.types.message import MessageEmbed, MessageTable
from disco.types.user import Game as DiscoGame
from disco.types.user import GameType, Status
from holster.emitter import Priority

from referee import ENV, STARTED
from referee.constants import (CONTROL_CHANNEL, PLAYING_STATUS, PY_CODE_BLOCK,
                               CommandLevel, check_global_admin,
                               get_user_level)
from referee.db import database, init_db
from referee.models.game import Game
from referee.plugins import GameManager, UserManager


class Core(Plugin):
    """
    Core plugin handling core bot features
    """

    BOT_DESC = 'Referee is a bot built to manage gaming communities'

    def load(self, ctx):
        init_db(ENV)

    plugins = {
        'gamemanager': GameManager.GameManager,
        'usermanager': UserManager.UserManager
    }

    @Plugin.listen('Ready', priority=Priority.BEFORE)
    def on_ready(self, event):
        """Fired when bot is ready, sets playing status"""
        self.client.update_presence(Status.invisible, DiscoGame(type=GameType.default, name=PLAYING_STATUS))
        with self.send_control_message() as embed:
            embed.title = 'Connected'
            embed.color = 0x77dd77

    @Plugin.listen('MessageCreate')
    def on_message_create(self, event):
        if event.message.author.bot:
            return

        commands = list(self.bot.get_commands_for_message(
            self.bot.config.commands_require_mention,
            self.bot.config.commands_mention_rules,
            self.bot.config.commands_prefix,
            event.message
        ))

        if not len(commands):
            return

        global_admin = check_global_admin(event.author.id)

        user_level = get_user_level(event.guild.members[event.author.id])

        for command, match in commands:
            if command.level == -1 and not global_admin:
                continue

            if not global_admin and command.level > user_level:
                continue

            try:
                command_event = CommandEvent(command, event.message, match)
                command.plugin.execute(command_event)
            except:
                self.log.exception('Command error:')

                with self.send_control_message() as embed:
                    embed.title = u'Command Error: {}'.format(command.name)
                    embed.color = 0xf3733a
                    embed.add_field(
                        name='Author', value='({}) `{}`'.format(event.author, event.author.id), inline=True)
                    embed.add_field(name='Channel', value='({}) `{}` in {}'.format(
                        event.channel.name if event.guild else event.channel.recipients.itervalues().next(),
                        event.channel.id,
                        event.guild.name if event.guild else 'a DM'
                    ), inline=True)
                    embed.description = '```{}```'.format(u'\n'.join(traceback.format_exc().split('\n')[-8:]))

                return event.reply('Something went wrong, perhaps try again another time!')

    @contextlib.contextmanager
    def send_control_message(self):
        embed = MessageEmbed()
        embed.set_footer(text='Referee')
        embed.timestamp = datetime.utcnow().isoformat()
        embed.color = 0x779ecb
        try:
            yield embed
            self.bot.client.api.channels_messages_create(
                CONTROL_CHANNEL,
                embed=embed
            )
        except:
            self.log.exception('Failed to send control message:')
            return

    @Plugin.command('commands')
    def commands_command(self, event):
        """Get a list of commands you can use with the bot"""
        embed = MessageEmbed()
        embed.set_author(
            name='Referee Commands',
            url='https://github.com/UHCBot/Referee',
            icon_url=self.client.state.me.avatar_url
        )
        embed.color = 0xf3733a
        for p in self.bot.plugins.values():
            for c in p.commands:
                args = []
                if c.args:
                    for arg in c.args.args:
                        args.append(arg.name)
                user_level = get_user_level(event.guild.members[event.msg.author.id])
                global_admin = check_global_admin(event.msg.author.id)
                if c.level:
                    if not global_admin and c.level == -1:
                        continue
                    if not global_admin and c.level > user_level:
                        continue
                embed.add_field(
                    name='{}{}'.format(
                        c.group + ' ' if c.group else '', c.name),
                    value='Level: {} {}\nArgs: {}\nDescription: {}'.format(
                        c.level if c.level else 'Everyone',
                        'or higher' if c.level and c.level != -1 else '',
                        ', '.join(args) if args != [] else 'None',
                        c.get_docstring() if c.get_docstring() else 'No description provided'
                    ).replace('-1', 'Global admin').replace('mod', 'Mod').replace('dev', 'Dev'),
                    inline=True
                    )
        event.msg.reply('', embed=embed)

    @Plugin.command('about')
    def about_command(self, event):
        """Gets some basic info about the bot"""
        embed = MessageEmbed()
        embed.set_author(name='Referee', icon_url=self.client.state.me.avatar_url, url='https://github.com/UHCBot/Referee')
        embed.description = self.BOT_DESC
        embed.add_field(name='Uptime', value=humanize.naturaldelta(datetime.utcnow() - STARTED), inline=True)
        embed.description = self.BOT_DESC
        embed.color = 0xf3733a

        event.msg.reply(embed=embed)

    @Plugin.command('reload', parser=True, level=-1)
    @Plugin.parser.add_argument('plugin', type=str, nargs='?', default='all')
    def on_reload_command(self, event, args):
        """Reloads a plugin"""
        if args.plugin == 'all':
            reloaded_plugins = ''
            for name, value in self.plugins.iteritems():
                self.bot.reload_plugin(value)
                event.msg.reply('Reloaded ' + name)
                reloaded_plugins += '{}\n'.format(name)
            with self.send_control_message() as embed:
                embed.title = "Plugins reloaded"
                embed.description = reloaded_plugins
            return

        if args.plugin.lower() in self.plugins:
            plugin = self.plugins[args.plugin.lower()]
            self.bot.reload_plugin(plugin)
            with self.send_control_message() as embed:
                embed.title = "Plugin reloaded"
                embed.description = args.plugin
            event.msg.reply('Reloaded ' + args.plugin)
        else:
            event.msg.reply('Couldn\'t find that plugin! Check your spelling!')

    @Plugin.command('uptime', level=CommandLevel.MOD)
    def uptime_command(self, event):
        """Gets the bots uptime"""
        event.msg.reply('Bot was started {} ago'.format(
            humanize.naturaldelta(datetime.utcnow() - STARTED)))

    @Plugin.command('ping', level=CommandLevel.MOD)
    def ping_command(self, event):
        """Tests bots ping"""
        recieved = datetime.utcnow()
        msg = event.msg.reply('Pinging!')
        replied = datetime.utcnow()
        diff = (replied - recieved)
        msg.edit('Pong! Took {} ms!'.format(diff.microseconds / 1000))

    @Plugin.command('reconnect', level=-1)
    def reload_command(self, event):
        """Reconnects the bot"""
        event.msg.reply('Okay! Closing connection')
        self.client.gw.ws.close()

    @Plugin.command('up', group='db', level=-1, conditional=lambda e: e.msg.attachments != [])
    def db_up(self, event):
        """Upload a JSON file to the DB"""
        games_json = {}
        found_game = False
        for attachment in event.msg.attachments.values():
            if '.json' in attachment.filename.lower():
                found_game = True
                response = requests.get(attachment.url)
                games_json = response.json()
                for game in games_json:
                    if not Game.get_game_by_name(game):
                        game_name = game
                        game = games_json[game]
                        Game.create(
                            name=game_name,
                            alias=game['alias'],
                            desc=game['desc'],
                            join_role=game['join_role'],
                            time_message=game['time_msg'],
                            a_channel=game['a_channel'],
                            a_message=game['a_message'],
                            interval=game['interval'],
                            attendees=game['attendees'],
                            join_src=game['join_src'],
                            play_src=game['play_src'],
                            last_announcement=datetime.utcnow()
                        )
                        event.msg.reply('Created game {}'.format(game_name))
                    else:
                        event.msg.reply('Game {} already existed.'.format(game))
                event.msg.reply('Done')
        if not found_game:
            event.msg.reply('You need to upload a JSON file!')

    @Plugin.command('down', group='db', level=-1)
    def db_down(self, event):
        """Download all games in the DB as JSON file"""
        games_json = {}
        games = Game.select()
        for game in games: # type: Game
            game_json = {
                'alias': game.alias,
                'desc': game.desc,
                'join_role': game.join_role,
                'time_msg': game.time_message,
                'a_channel': game.a_channel,
                'a_message': game.a_message,
                'interval': game.interval,
                'attendees': game.attendees,
                'join_src': game.join_src,
                'play_src': game.play_src
            }
            games_json[game.name] = game_json
        event.msg.reply('Here is your file!', attachments=[('database.json', json.dumps(games_json))])

    @Plugin.command('sql', level=-1)
    def sql_command(self, event):
        conn = database.obj.get_conn()
        try:
            tbl = MessageTable(codeblock=False)

            with conn.cursor() as cur:
                start = time.time()
                cur.execute(event.codeblock.format(e=event))
                dur = time.time() - start
                if cur.description:
                    tbl.set_header(*[desc[0] for desc in cur.description])

                    for row in cur.fetchall():
                        tbl.add(*row if row else '')

                result = tbl.compile()
                if len(result) > 1900:
                    return event.msg.reply(
                        '_took {}ms_'.format(int(dur * 1000)),
                        attachments=[('result.txt', result)])
                elif len(result) == 0:
                    result = '\n'

                event.msg.reply('```' + result + '```\n_took {}ms_\n'.format(int(dur * 1000)))
        except psycopg2.Error as e:
            event.msg.reply('```{}```'.format(e.pgerror))

    @Plugin.command('eval', level=-1)
    def eval_command(self, event):
        ctx = {
            'self': self,
            'bot': self.bot,
            'client': self.bot.client,
            'state': self.bot.client.state,
            'event': event,
            'msg': event.msg,
            'guild': event.msg.guild,
            'channel': event.msg.channel,
            'author': event.msg.author
        }

        # Mulitline eval
        src = event.codeblock
        if src.count('\n'):
            lines = filter(bool, src.split('\n'))
            if lines[-1] and 'return' not in lines[-1]:
                lines[-1] = 'return ' + lines[-1]
            lines = '\n'.join('    ' + i for i in lines)
            code = 'def f():\n{}\nx = f()'.format(lines)
            local = {}

            try:
                exec compile(code, '<eval>', 'exec') in ctx, local
            except Exception as e:
                event.msg.reply(PY_CODE_BLOCK.format(type(e).__name__ + ': ' + str(e)))
                return

            result = pprint.pformat(local['x'])
        else:
            try:
                result = str(eval(src, ctx))
            except Exception as e:
                event.msg.reply(PY_CODE_BLOCK.format(type(e).__name__ + ': ' + str(e)))
                return

        if len(result) > 1990:
            event.msg.reply('', attachments=[('result.txt', result)])
        else:
            event.msg.reply(PY_CODE_BLOCK.format(result))
