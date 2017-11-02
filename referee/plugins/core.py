"""Core handler for bot"""
import contextlib
import pprint
import time
import traceback
from datetime import datetime

import humanize
import psycopg2
from disco.bot import Bot, Plugin
from disco.bot.command import CommandEvent
from disco.types.message import MessageEmbed, MessageTable
from disco.types.user import Game, GameType, Status

from referee import ENV, STARTED
from referee.constants import (CONTROL_CHANNEL, PLAYING_STATUS, PY_CODE_BLOCK,
                               check_global_admin)
from referee.db import database, init_db


class Core(Plugin):
    """
    Core plugin handling core bot features
    """

    @Plugin.listen('Ready')
    def on_ready(self, event):
        """Fired when bot is ready, sets playing status"""
        self.client.update_presence(Status.online, Game(type=GameType.default, name=PLAYING_STATUS))
        with self.send_control_message() as embed:
            embed.title = 'Connected'
            embed.color = 0x77dd77

    @Plugin.listen('MessageCreate')
    def on_message_create(self, event):
        if event.message.author.bot:
            return

        if hasattr(event, 'guild') and event.guild:
            guild_id = event.guild.id
        elif hasattr(event, 'guild_id') and event.guild_id:
            guild_id = event.guild_id
        else:
            guild_id = None

        commands = list(self.bot.get_commands_for_message(
            self.bot.config.commands_require_mention,
            self.bot.config.commands_mention_rules,
            self.bot.config.commands_prefix,
            event.message
        ))

        if not len(commands):
            return

        global_admin = check_global_admin(event.author.id)

        for command, match in commands:
            if command.level == -1 and not global_admin:
                continue

            if not self.bot.check_command_permissions(command, event):
                continue

            try:
                command_event = CommandEvent(command, event.message, match)
                command.plugin.execute(command_event)
            except:

                self.log.exception('Command error:')

                with self.send_control_message() as embed:
                    embed.title = u'Command Error: {}'.format(command.name)
                    embed.color = 0xff6961
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

    @Plugin.command('uptime')
    def uptime_command(self, event):
        if check_global_admin(event.msg.author.id):
            event.msg.reply('Bot was started {} ago'.format(
                humanize.naturaldelta(datetime.utcnow() - STARTED)))

    @Plugin.command('reconnect')
    def reload_command(self, event):
        if check_global_admin(event.msg.author.id):
            event.msg.reply('Okay! Closing connection')
            self.client.gw.ws.close()

    @Plugin.command('sql')
    def sql_command(self, event):
        if not check_global_admin(event.msg.author.id):
            return
        conn = database.obj.get_conn()
        try:
            tbl = MessageTable(codeblock=False)

            with conn.cursor() as cur:
                start = time.time()
                cur.execute(event.codeblock.format(e=event))
                dur = time.time() - start
                tbl.set_header(*[desc[0] for desc in cur.description])

                for row in cur.fetchall():
                    tbl.add(*row)

                result = tbl.compile()
                if len(result) > 1900:
                    return event.msg.reply(
                        '_took {}ms_'.format(int(dur * 1000)),
                        attachments=[('result.txt', result)])

                event.msg.reply('```' + result + '```\n_took {}ms_\n'.format(int(dur * 1000)))
        except psycopg2.Error as e:
            event.msg.reply('```{}```'.format(e.pgerror))

    @Plugin.command('eval')
    def eval_command(self, event):
        if not check_global_admin(event.msg.author.id):
            return
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
