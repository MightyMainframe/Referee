"""Manages all game related bits"""
import gevent
from disco.bot import Plugin

from referee.constants import GAME_ADD_STEPS, GAME_INFO_STEPS, check_global_admin
from referee.models.game import Game


class GameManager(Plugin):
    """Manages all game related bits"""
    def add_game(self, event, name, desc, create_channels=False):
        """
        Sets up a new game
        """
        if create_channels:
            #Create channels
            channel_name = name.replace(' ', '-')
            guild = event.msg.guild
            category = guild.create_category(channel_name)
            ac = category.create_text_channel('announcements')
            ac.topic = desc

        Game.new(name=name, desc=desc, ac=ac.id if create_channels else None)

    @Plugin.command('add', group='game')
    def add_command(self, event):
        """Gets all info required for creation a new game"""
        if not check_global_admin(event.msg.author.id):
            return

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
