from sys import stdout, stderr
import os
import argparse
import subprocess
from db import Database
from config import parse_config

import commands.switch

from commands import parse_date_time

parser = argparse.ArgumentParser(add_help=False,
    description='Put an entry into the current timesheet')

parser.add_argument('--switch', '-s', default=None,
    help='sheet to switch to before starting the timer')

parser.add_argument('start_time', help='start time')

parser.add_argument('end_time', help='end time')

parser.add_argument('messages', nargs='*', default='',
    help='status message')

aliases=['p']

def command(timebook, config, switch, start_time, end_time, messages, **kwargs):
    # get the db
    cfg=parse_config(config)
    db=Database(timebook, cfg)

    if switch:
        commands.switch.switch(db, switch)
        sheet = switch
    else:
        sheet = db.get_current_sheet()

    timestamp_in=parse_date_time(start_time)
    timestamp_out=parse_date_time(end_time)

    current_start = db.get_start_time(sheet)
    if current_start:
        if timestamp_out > current_start[1]:
            parser.error('cannot put this entry into the timesheet because ' \
                'it may cause overlap with the active timer - clock out first')

    message = ' '.join(messages)

    put(db, sheet, timestamp_in, timestamp_out, message)

def put(db, sheet, timestamp_in, timestamp_out, message):
    """
    put an entry into the specified timesheet
    """
    if timestamp_out < timestamp_in:
        parser.error('start time is after end time')

    db.execute('''
    select
        count(*)
    from
        entry
        where sheet = ?
        and(
            ((? >= start_time) and (? < end_time))
            or((? >= start_time) and (? < end_time))
            or((? < start_time) and (? >= end_time))
        )
    ''', (sheet,
         timestamp_in, timestamp_in,
         timestamp_out, timestamp_out,
         timestamp_in, timestamp_out))

    if db.fetchone()[0] > 0:
        parser.error('entry would cause overlap')

    db.execute('''
    insert into entry (
        sheet, start_time, end_time, description
    ) values (?,?,?,?)
    ''', (sheet, timestamp_in, timestamp_out, message))

