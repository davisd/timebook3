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

parser.add_argument('--sheet', '-s', default=None,
    help='sheet to clock out of')

aliases=['o', 'stop']

def command(timebook, config, at, sheet, **kwargs):
    # get the db
    cfg=parse_config(config)
    db=Database(timebook, cfg)

    timestamp=parse_date_time_or_now(at)

    sheet = sheet or db.get_current_sheet()

    if sheet not in db.get_sheet_names():
        parser.error('%s is not a known timesheet' % sheet)

    out(db, timestamp, sheet)

def out(db, timestamp, sheet=None):
    """
    stop the timer for an entry
    """
    if not sheet:
        active=db.get_current_active_info()
    else:
        active=db.get_active_info(sheet)

    if not active:
        parser.error('the timesheet is not active')
    active_id, start_time = active

    active_time = timestamp - start_time
    if active_time < 0:
        parser.error('negative active time')

    db.execute('''
    update
        entry
    set
        end_time = ?
    where
        entry.id = ?
    ''', (timestamp, active_id))

