from sys import stdout, stderr
import os
import argparse
from datetime import timedelta
from db import Database
from config import parse_config

from commands import parse_date_time, parse_date_time_or_now

from output import format_report

parser = argparse.ArgumentParser(add_help=False,
    description='Display totaled data from timesheets')

parser.add_argument('--start', '-s',
    help='show only entries starting on or after this date. Should be ' \
        'in the format YY-MM-DD hh:mm:ss')

parser.add_argument('--end', '-e',
    help='show only entries ending before this date. Should be ' \
        'in the format YY-MM-DD hh:mm:ss')

parser.add_argument('--billing', '-b', action='store_true',
    help='only show entries in the current billing cycle')

parser.add_argument('--money', '-m', action='store_true', default=False,
            help='display amounts based on rate and duration')

aliases=['f']

def command(timebook, config, start, end, billing, money, **kwargs):
    # get the db
    cfg=parse_config(config)
    db=Database(timebook, cfg)

    start_timestamp = parse_date_time(start) if start else None
    end_timestamp = parse_date_time(end) if end else None

    full(db, start_timestamp, end_timestamp, billing, money)

def full(db, start, end, billing, money):
    """
    display totaled data from timesheets
    """
    format_report(db, start, end, billing, money)

