from sys import stdout, stderr
import os
import argparse
from datetime import timedelta
from db import Database
from config import parse_config

from commands import parse_date_time, parse_date_time_or_now

from output import format_timebook, format_csv

parser = argparse.ArgumentParser(add_help=False,
    description='Display the timesheet, by default the current one')

parser.add_argument('--start', '-s',
    help='show only entries starting on or after this date. Should be ' \
        'in the format YY-MM-DD hh:mm:ss')

parser.add_argument('--end', '-e',
    help='show only entries ending before this date. Should be ' \
        'in the format YY-MM-DD hh:mm:ss')

parser.add_argument('--billing', '-b', action='store_true',
    help='only show entries in the current billing cycle')

parser.add_argument('--format', '-f', default='plain', choices=['plain', 'csv'],
    help='display format')

parser.add_argument('--money', '-m', action='store_true', default=False,
            help='display amounts based on rate and duration')

parser.add_argument('sheet', nargs='?',
    help='sheet to display (by deafult the current one)')

aliases=['d', 'export', 'format', 'show']

def command(timebook, config, sheet, start, end, billing, format, money, **kwargs):
    # get the db
    cfg=parse_config(config)
    db=Database(timebook, cfg)

    sheet = sheet or db.get_current_sheet()

    start_timestamp = parse_date_time(start) if start else None
    end_timestamp = parse_date_time(end) if end else None

    if billing:
        if start or end:
            parser.error('if you specify --billing, you cannot specify a start ' \
                'or end ')

        billing_time = db.get_billing_start_time(sheet)

        if billing_time:
            start_timestamp = billing_time

    display(db, sheet, start_timestamp, end_timestamp, format, money)

def display(db, sheet, start, end, format, money):
    """
    display the timesheet
    """
    sheet = sheet or db.get_current_sheet()

    if format=='plain':
        format_timebook(db, sheet, start, end, money)
    elif format=='csv':
        format_csv(db, sheet, start, end)


