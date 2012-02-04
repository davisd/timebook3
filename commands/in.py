from sys import stdout, stderr
import os
import argparse
import subprocess
from db import Database
from config import parse_config

import commands.switch
import commands.out

from commands import parse_date_time_or_now

parser = argparse.ArgumentParser(add_help=False,
    description='Start the timer on a sheet')

parser.add_argument('--switch', '-s', default=None,
    help='sheet to switch to before starting the timer')

parser.add_argument('--out', '-o', action='store_true', default=False,
    help='clock out before clocking in')

parser.add_argument('--at', '-a', default=None,
    help='clock in time')

message_parser = parser.add_mutually_exclusive_group()
message_parser.add_argument('--resume', '-r', action='store_true', default=False,
    help='use the same status message as last active period')
message_parser.add_argument('messages', nargs='*', default='',
    help='status message')

aliases=['i', 'start']

def command(timebook, config, switch, out, at, resume, messages, **kwargs):
    # get the db
    cfg=parse_config(config)
    db=Database(timebook, cfg)

    if switch:
        commands.switch.switch(db, switch)
        sheet = switch
    else:
        sheet = db.get_current_sheet()

    timestamp=parse_date_time_or_now(at)

    if out:
        commands.out.out(db, timestamp)

    if db.get_active_info(sheet):
        parser.error('the timesheet is already active')

    message = ' '.join(messages)

    most_recent_clockout = db.get_most_recent_clockout(sheet)
    if most_recent_clockout:
        (previous_timestamp, previous_description) = most_recent_clockout
        if timestamp < previous_timestamp:
            parser.error('error: time periods could end up overlapping')
        if resume:
            if message:
                parser.error('"--resume" sets the note, so you cannot also ' \
                    'supply the message')
            message = previous_description

    _in(db, sheet, timestamp, message)

def _in(db, sheet, timestamp, message):
    """
    start the timer on a sheet
    """
    db.execute('''
        insert into entry (
            sheet, start_time, description
        ) values (?,?,?)
        ''', (sheet, timestamp, message))

