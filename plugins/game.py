from disco.bot import Plugin
import gevent
from constants import check_global_admin

class GameManager(Plugin):
    @Plugin.command('add', group='game')
    def add_command(self, event):
        if not check_global_admin(event.msg.author.id):
            return

        messages_to_delete = []

        def remove_messages():
            for message in messages_to_delete:
                event.msg.channel.get_message(message).delete()

        msg = event.msg
        confirm_msg = msg.reply('This will start the proces of {}. Is this correct?'.format(
            'creating a new game',
        ))
        messages_to_delete.append(msg.id)
        messages_to_delete.append(confirm_msg.id)
        try:
            message = self.wait_for_event(
                'MessageCreate',
                conditional=lambda e: (
                    (e.message.content.lower() == 'y' or e.message.content.lower() == 'yes') and 
                    e.message.author == msg.author
                )
            ).get(timeout=30)
            messages_to_delete.append(message.id)
        except gevent.Timeout:
            fail_msg = msg.reply('Request timed out!')
            messages_to_delete.append(fail_msg.id)
            remove_messages()
            return
        
        give_name = msg.reply('Okay, please give the name of the new game')
        messages_to_delete.append(give_name.id)
        try:
            game_name_msg = self.wait_for_event(
                'MessageCreate',
                conditional=lambda e: (
                    e.message.author == msg.author
                )
            ).get(timeout=30)
            messages_to_delete.append(game_name_msg.id)
        except gevent.Timeout:
            fail_msg = msg.reply('Request timed out!')
            messages_to_delete.append(fail_msg.id)
            remove_messages()
            return
        game_name = game_name_msg.content
        print game_name
        msg.reply('Wew!')
