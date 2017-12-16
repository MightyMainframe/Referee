"""
Constants for usage throughout the entire bot
If you plan to self host this bot, edit them to contain values from your server
"""
import re
from collections import OrderedDict
from holster.enum import Enum

###Constants
CONTROL_CHANNEL = 375605052171354122
PLAYING_STATUS = 'Managing all the things'
GLOBAL_ADMINS = [188918216008007680, 134146475591467008]
MOD_ROLE = 370594147511566336
DEV_ROLE = 294473442164604929
PY_CODE_BLOCK = u'```py\n{}\n```'
TEAM_CATEGORY = 355983461825380352
REACTIONS_MESSAGES = [382172474076430337, 382173174525198336]
EMOJIS = {
    377098801095114753: u'MMTestGame',
    377098801195909122: u'MMOW',
    377098801384652800: u'MMUHC',
    377098801397235722: u'MMRL',
    377098801573527564: u'MMPUBGHelmet',
    377099565033062400: u'MMMC',
    377100326655885312: u'MMEvening',
    377100326731251712: u'MMMorning',
    379104082079514637: u'MMTeamAqua',
    379104082461458432: u'MMTeamGreen',
    379104087679041538: u'MMTeamGold',
    379104088098471956: u'MMTeamYellow',
    379104088102535169: u'MMTeamRed',
    379104088111185920: u'MMTeamPurple',
    379104088111185922: u'MMTeamPink',
    379104088232558592: u'MMTeamOrange',
    379104088257724416: u'MMTeamBlue',
    379104088442535946: u'MMTeamDarkRed',
    381430584154652673: u'MMPUBG'
}
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
LEVELS = {
    50: 382587056356065312,
    110: 382586765372030976,
    250: 382587226023919618
}

###Enums

CommandLevel = Enum(
    MOD=2,
    DEV=1
)

###Functions
def check_global_admin(uid):
    """Checks if user is global admin and thus can use all commands"""
    return bool(uid in GLOBAL_ADMINS)

def get_user_level(user):
    """Gets user level for certain user"""
    user = user
    if MOD_ROLE in user.roles:
        return 2
    elif DEV_ROLE in user.roles:
        return 1
    else:
        return 0

###Regexes
BATTLE_TAG = re.compile(r'^[a-z][a-z0-9]{2,11}#[0-9]{4,5}', re.I)
MC_NAME = re.compile(r'[a-z0-9_]{1,16}', re.I)
MC_UUID = re.compile(r'[0-9a-f]{32}')
STEAM_NAME = re.compile(r'[a-z0-9_]{3,}', re.I)
