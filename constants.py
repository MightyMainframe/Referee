"""
Constants for usage throughout the entire bot
If you plan to self host this bot, edit them to contain values from your server
"""
import re
from collections import OrderedDict

###Constants
PLAYING_STATUS = 'Managing all the things'
GLOBAL_ADMINS = [188918216008007680, 134146475591467008, 125793782665969664]
PY_CODE_BLOCK = u'```py\n{}\n```'
GAME_INFO_STEPS = OrderedDict([
    ('get_name', 'Okay, please give the name of the new game'),
    ('get_desc', 'Okay, created the game. now, give a description for the game'),
    ('should_create_channels', 'Should I create channels for this game?')
])
GAME_ADD_STEPS = {
    'validate': 'This will start the proces of {}. Is this correct?'.format(
        'creating a new game',
    ),
    'complete': 'Created game `{}`, with description `{}`. I `will{}` create channels for it.',
    'fail': 'Process canceled. Restart it by using `!game add`'
}
MC_UUID_URL = 'https://api.mojang.com/users/profiles/minecraft/{}'

###Functions
def check_global_admin(uid):
    """Checks if user is global admin and thus can use all commands"""
    return bool(uid in GLOBAL_ADMINS)

###Regexes
BATTLE_TAG = re.compile(r'^[a-z][a-z0-9]{2,11}#[0-9]{4,5}', re.I)
MC_NAME = re.compile(r'[a-z0-9_]{1,16}', re.I)
MC_UUID = re.compile(r'[0-9a-f]{32}')
STEAM_NAME = re.compile(r'[a-z0-9_]{3,}', re.I)
