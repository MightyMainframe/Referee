from disco.bot import Plugin

from referee.plugins import Core, GameManager, UserManager

class Reloader(Plugin):
    """
    Plugin that will reload other plugins
    """

    plugins = {
        'gamemanager': GameManager.GameManager,
        'usermanager': UserManager.UserManager
    }

    @Plugin.command('reload', parser=True, level=-1)
    @Plugin.parser.add_argument('plugin', type=str, nargs='?', default='all')
    def on_reload_command(self, event, args):
        if args.plugin == 'all':
            for name, value in self.plugins.iteritems():
                self.bot.reload_plugin(value)
                event.msg.reply('Reloaded ' + name)
            return

        if args.plugin.lower() in self.plugins:
            plugin = self.plugins[args.plugin]
            self.bot.reload_plugin(plugin)
            event.msg.reply('Reloaded ' + args.plugin)
        else:
            event.msg.reply('Couldn\'t find that plugin! Check your spelling!')
