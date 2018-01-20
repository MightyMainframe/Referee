#!/usr/bin/env python
from gevent import monkey; monkey.patch_all()

from werkzeug.serving import run_with_reloader
from gevent import wsgi
from referee.db import init_db
from referee import ENV
from referee.web import referee
from disco.util.logging import LOG_FORMAT
from yaml import load

import os
import copy
import click
import signal
import logging
import gevent
import subprocess

class BotSupervisor(object):
    def __init__(self, env={}):
        self.proc = None
        self.env = env
        self.bind_signals()
        self.start()

    def bind_signals(self):
        signal.signal(signal.SIGUSR1, self.handle_sigusr1)

    def handle_sigusr1(self, signum, frame):
        print 'SIGUSR1 - RESTARTING'
        gevent.spawn(self.restart)

    def start(self):
        env = copy.deepcopy(os.environ)
        env.update(self.env)
        self.proc = subprocess.Popen(['python', '-m', 'disco.cli', '--config', 'config.yaml'], env=env)

    def stop(self):
        self.proc.terminate()

    def restart(self):
        try:
            self.stop()
        except:
            pass

        self.start()

    def run_forever(self):
        while True:
            self.proc.wait()
            gevent.sleep(5)


@click.group()
def cli():
    logging.getLogger().setLevel(logging.INFO)


@cli.command()
@click.option('--env', '-e', default='local')
def bot(env):
    supervisor = BotSupervisor(env={
        'ENV': env
    })
    supervisor.run_forever()

@cli.command()
@click.option('--reloader/--no-reloader', '-r', default=False)
def web(reloader):
    def run():
        wsgi.WSGIServer(('0.0.0.0', 8686), referee.app).serve_forever()

    if reloader:
        run_with_reloader(run)
    else:
        run()

@cli.command('add-global-admin')
@click.argument('uid')
def add_global_admin(uid):
    from referee.db import rdb
    init_db(ENV)
    rdb.sadd('global_admins', uid)
    print 'Ok, aded {} as a global admin!'.format(uid)


if __name__ == '__main__':
    cli()
