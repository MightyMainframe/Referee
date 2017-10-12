"""Core handler for bot"""
import pprint

from datetime import datetime

import humanize

from disco.bot import Plugin
from disco.types.user import Game, Status, GameType
from constants import (
    PLAYING_STATUS, GLOBAL_ADMINS, PY_CODE_BLOCK, check_global_admin
)

class CorePlugin(Plugin):
    """
    Core plugin handling core bot features
    """
    def load(self, ctx):
        super(CorePlugin, self).load(ctx)
        self.started = datetime.utcnow()

    @Plugin.listen('Ready')
    def on_ready(self, event):
        """Fired when bot is ready, sets playing status"""
        self.client.update_presence(Status.invisible, Game(type=GameType.default, name=PLAYING_STATUS))

    @Plugin.command('uptime')
    def uptime_command(self, event):
        if check_global_admin(event.msg.author.id):
            event.msg.reply('Bot was started {} ago'.format(
                humanize.naturaldelta(datetime.utcnow() - self.started)))

    @Plugin.command('eval')
    def eval_command(self, event):
        if not check_global_admin(event.msg.author.id):
            return
        ctx = {
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

