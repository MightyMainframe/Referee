from disco.bot import Plugin
import gevent
from constants import check_global_admin

class GameManager(Plugin):
    @Plugin.command('add', '<name:str>, <description:str...>', group='game')
    def add_command(self, event, name, description):
        if not check_global_admin(event.msg.author.id):
            return

        msg = event.msg
        confirm_msg = msg.reply('This will start the proces of creating a new game with name {}. Is this correct?'.format(name))
        try:
            message = self.wait_for_event(
                'MessageCreate',
                conditional=lambda e: (
                    (e.message.content == 'y' or e.message.content == 'yes') and 
                    e.message.author == msg.author
                )
            ).get(timeout=30)
        except gevent.Timeout:
            fail_msg = msg.reply('Request timed out!')
            fail_msg.delete()
            msg.delete()
            confirm_msg.delete()
            if message:
                message.delete()
            return

        msg.reply('wew')
