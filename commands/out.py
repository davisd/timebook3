from sys import stdout, stderr
import os
import argparse
import subprocess
from db import Database
from config import parse_config

import commands.out

from commands import parse_date_time_or_now

parser = argparse.ArgumentParser(add_help=False,
    description='Stop the timer for a sheet')

parser.add_argument('--at', '-a', default=None,
    help='clock out time')

aliases=['o', 'stop']

def command(timebook, config, at, **kwargs):
    # get the db
    cfg=parse_config(config)
    db=Database(timebook, cfg)

    timestamp=parse_date_time_or_now(at)

    out(db, timestamp)

def out(db, timestamp):
    """
    stop the timer for an entry
    """
    active = db.get_current_start_time()
    if not active:
        parser.error('the timesheet is not active')
    active_id, start_time = active

    active_time = timestamp - start_time
    if active_time < 0:
        parserr.error('negative active time')

    db.execute('''
    update
        entry
    set
        end_time = ?
    where
        entry.id = ?
    ''', (timestamp, active_id))

