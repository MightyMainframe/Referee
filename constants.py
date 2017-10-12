"""
Constants for usage throughout the entire bot
If you plan to self host this bot, edit them to contain values from your server
"""

PLAYING_STATUS = 'Managing the <name>'
GLOBAL_ADMINS = [188918216008007680, 134146475591467008, 125793782665969664]
PY_CODE_BLOCK = u'```py\n{}\n```'

def check_global_admin(uid):
    """Checks if user is global admin and thus can use all commands"""
    return bool(uid in GLOBAL_ADMINS)
