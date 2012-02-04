from sys import stdout, stderr
import os
import argparse
import subprocess
from db import Database
from config import parse_config

parser = argparse.ArgumentParser(add_help=False,
    description='Alter the description of the current period')

parser.add_argument('messages', nargs='*', default='',
    help='status message')

aliases=['a', 'write']

def command(timebook, config, messages, **kwargs):
    # get the db
    cfg=parse_config(config)
    db=Database(timebook, cfg)

    active = db.get_current_active_info()
    if not active:
        parser.error('timesheet not active')

    entry_id=active[0]
    message = ' '.join(messages)
    alter(db, entry_id, message)

def alter(db, entry_id, message):
    """
    alter the description of the specified entry
    """
    db.execute('''
    update
        entry
    set
        description = ?
    where
        entry.id = ?
    ''', (message,entry_id))

