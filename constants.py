"""
Constants for usage throughout the entire bot
If you plan to self host this bot, edit them to contain values from your server
"""
from collections import OrderedDict

###Constants
PLAYING_STATUS = 'Managing the <name>'
GLOBAL_ADMINS = [188918216008007680, 134146475591467008, 125793782665969664]
PY_CODE_BLOCK = u'```py\n{}\n```'
INFO_STEPS = OrderedDict([
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

###Functions
def check_global_admin(uid):
    """Checks if user is global admin and thus can use all commands"""
    return bool(uid in GLOBAL_ADMINS)
