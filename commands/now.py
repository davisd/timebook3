from sys import stdout, stderr
import os
import argparse
from datetime import timedelta
from db import Database
from config import parse_config

from output import pprint_table

parser = argparse.ArgumentParser(add_help=False,
    description='Show the status of the current timesheet')

parser.add_argument('--simple', '-s', action='store_true', default=False,
    help='only display the name of the current timesheet')

parser.add_argument('--notes', '-n', action='store_true', default=False,
    help='only display the notes associated with the current period')

parser.add_argument('sheet', nargs='?',
    help='display information for this timesheet instead')

aliases=['n', 'info']

def command(timebook, config, simple, notes, sheet, **kwargs):
    # get the db
    cfg=parse_config(config)
    db=Database(timebook, cfg)

    if simple and notes:
        parser.error('you cannot specify both --simple and --notes')

    now(db, simple, notes, sheet)

def now(db, simple, _notes, sheet):
    """
    show the status of a timesheet
    """
    sheet = sheet or db.get_current_sheet()
    if simple:
        print(sheet)
        return

    entry_count = db.get_entry_count(sheet)
    if entry_count == 0:
        parser.error('sheet is empty')

    running = db.get_active_info(sheet)
    notes = ''
    if running is None:
        active = 'not active'
    else:
        duration = str(timedelta(seconds=running[0]))
        if running[1]:
            notes = running[1].rstrip('.')
            active = '%s (%s)' % (duration, notes)
        else:
            active = duration
    if _notes:
        print(notes)
    else:
        print('%s: %s' % (sheet, active))


