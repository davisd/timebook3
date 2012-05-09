from sys import stdout, stderr
import os
import argparse
import subprocess
from db import Database
from config import parse_config

from commands import parse_date_time_or_now

parser = argparse.ArgumentParser(add_help=False,
    description='Start a new billing cycle for the current timesheet')

parser.add_argument('--at', '-a', default=None,
            help='time to start the new cycle')

parser.add_argument('--sheet', '-s', default=None,
    help='sheet to end')

aliases=['e', 'bill']

def command(timebook, config, at, sheet, **kwargs):
    # get the db
    cfg=parse_config(config)
    db=Database(timebook, cfg)

    sheet = sheet or db.get_current_sheet()
    timestamp = parse_date_time_or_now(at)

    if sheet not in db.get_sheet_names():
        parser.error('%s is not a known timesheet' % sheet)

    end(db, sheet, timestamp)

def end(db, sheet, start_time):
    """
    end the billing cycle for the timesheet and start a new billing cycle

    sheet - timesheet
    start_time - start time for the new billing cycle
    """
    # if currently active, clock out
    active = db.get_active_info(sheet)
    if active:
        parser.error('the timesheet is currently active')

    db.execute('''
    replace into
        sheet_meta
            (sheet, billing_start_time, rate)
        values
            (?, ?, (select rate from sheet_meta where sheet = ?))
    ''', (sheet, start_time, sheet))

