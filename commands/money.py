from sys import stdout, stderr
import os
import argparse
import subprocess
from db import Database
from config import parse_config

from commands import parse_date_time_or_now

def currency(x):
    return int(float(x)*100)

parser = argparse.ArgumentParser(add_help=False,
    description='Set the billing rate for the current timesheet')

parser.add_argument('--sheet', '-s', default=None,
    help='sheet to set the rate for')

parser.add_argument('rate', type=currency,
    help='the new rate')

aliases=['m', 'rate']

def command(timebook, config, rate, sheet, **kwargs):
    # get the db
    cfg=parse_config(config)
    db=Database(timebook, cfg)

    sheet = sheet or db.get_current_sheet()
    if sheet not in db.get_sheet_names():
        parser.error('%s is not a known timesheet' % sheet)

    money(db, sheet, rate)

def money(db, sheet, rate):
    """
    set the billing rate for the current timesheet
    """
    db.execute('''
    replace into
        sheet_meta
            (sheet, rate, billing_start_time)
        values
            (?, ?, (select billing_start_time from sheet_meta where sheet = ?))
    ''', (sheet, rate, sheet))


