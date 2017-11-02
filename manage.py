#!/usr/bin/env python
from gevent import monkey; monkey.patch_all()

from werkzeug.serving import run_with_reloader
from gevent import wsgi
from referee.db import init_db
from disco.util.logging import LOG_FORMAT
from yaml import load

import os
import copy
import click
import signal
import logging
import gevent
import subprocess

from referee.db import init_db

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
        init_db()
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

if __name__ == '__main__':
    cli()