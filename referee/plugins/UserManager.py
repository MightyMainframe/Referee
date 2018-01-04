"""Manages all user related bits"""
import requests
from disco.bot import Plugin

from referee.constants import (BATTLE_TAG, LEVELS, MC_NAME, MC_UUID,
                               MC_UUID_URL, STEAM_NAME, CommandLevel)
from referee.models.user import User


def get_mc_uuid(username):
    """Gets the UUID for a MC username"""
    response = requests.get(MC_UUID_URL.format(username))
    if response.status_code == 204:
        return 'Oh no! Something went wrong! Double check your minecraft name and try again!'
    uuid = response.json()["id"]
    return uuid


def check_regex(regex):
    """Checks if a regex passed"""
    if not regex or not regex.string:
        return False
    elif regex.string == '':
        return False
    return True

class UserManager(Plugin):
    """Manages user related bits"""

    @Plugin.command('first', group='award', level=CommandLevel.MOD, context={'points': 10})
    @Plugin.command('second', group='award', level=CommandLevel.MOD, context={'points': 5})
    @Plugin.command('third', group='award', level=CommandLevel.MOD, context={'points': 2})
    def award_command(self, event, points=10):
        if not event.msg.mentions:
            event.msg.reply('Please mention all users you want to award the {} place'.format(
                event.command.name))
            return
        users = event.msg.mentions.values()
        for user in users:
            member = event.msg.member
            user = User.get_user_by_id(user.id) # type: User
            for level in LEVELS:
                if level < user.points + points and LEVELS[level] not in member.roles:
                    member.add_role(LEVELS[level])
            user.add_points(points)
        event.msg.reply('Okay! Points are awarded!')
        
    @Plugin.command('get', '<key:str>', group='metadata')
    def get_metadata(self, event, key):
        try:
            user = User.get_user_by_id(event.msg.author.id)
        except:
            return event.msg.reply('You don\'t have any data stored yet!')
        
        return event.msg.reply(user.get_metadata())

    @Plugin.command('add', '<key:str> <value:str>', aliases=['set', 'save'], group='metadata')
    def add_metadata(self, event, key, value):
        """Adds metadata to a user"""
        try:
            user = User.get_user_by_id(event.msg.author.id)
        except AttributeError:
            user = User.new(event.msg.author.id)

        key = key.lower()
        if not key in User.metadata_fields:
            return event.msg.reply('Couldn\'t add metadata. {} \n```{}```'.format(
                'You can add metadata for the following keys:',
                User.get_metadata_fields()
            ))
        if key == 'blizzard':
            tag = BATTLE_TAG.search(value)
            if not check_regex(tag):
                return event.msg.reply('Invalid battle tag provided!')
            tag = tag.string
            user.add_battle_tag(tag)
            return event.msg.reply('Okay! Added battle tag `{}` to your profile!'.format(tag))
        elif key == 'minecraft':
            name = MC_NAME.search(value)
            if not check_regex(name):
                return event.msg.reply('Invalid minecraft name provided')
            name = name.string
            uuid = get_mc_uuid(name)
            check = MC_UUID.search(uuid)
            if not check.string or check.string == '':
                event.msg.reply(uuid)
            uuid = check.string
            uuid = uuid[:8]+"-"+uuid[8:12]+"-"+uuid[12:16]+"-"+uuid[16:20]+"-"+uuid[20:]
            user.add_minecraft_data(name, uuid)
            return event.msg.reply('Okay! Added Minecraft name `{}` to your profile!'.format(name))
        elif key == 'steam':
            name = STEAM_NAME.search(value)
            if not check_regex(name):
                return event.msg.reply('Invalid steam name provided')
            name = name.string
            user.add_steam_name(name)
            return event.msg.reply('Okay! Added steam name `{}` to your profile!'.format(name))

    @Plugin.command('remove', '<key:str>', aliases=['delete', 'clear'], group='metadata')
    def remove_metadata(self, event, key):
        """Removes metadata from a user"""
        try:
            user = User.get_user_by_id(event.msg.author.id)
        except AttributeError:
            return event.msg.reply('No user found!')
        key = key.lower()
        if not key in User.metadata_fields:
            return event.msg.reply('Couldn\'t remove metadata. {} \n```{}```'.format(
                'You can remove metadata for the following keys:',
                User.get_metadata_fields()
            ))
        if key == 'blizzard':
            user.add_battle_tag('')
        elif key == 'minecraft':
            user.add_minecraft_data('', '')
        elif key == 'steam':
            user.add_steam_name('')
        return event.msg.reply('Okay! Removed metadata for `{}`!'.format(key))
