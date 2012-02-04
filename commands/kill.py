from sys import stdout, stderr
import os
import argparse
import subprocess
from db import Database
from config import parse_config

import commands.switch

parser = argparse.ArgumentParser(add_help=False,
    description='Delete a timesheet')

parser.add_argument('sheet', nargs='?', default=None,
    help='sheet to delete')

aliases=['k', 'delete']

def command(timebook, config, sheet, **kwargs):
    # get the db
    cfg=parse_config(config)
    db=Database(timebook, cfg)

    switch_to_default=False

    current_sheet = db.get_current_sheet()
    if not sheet or sheet == current_sheet:
        switch_to_default=True
    if not sheet:
        sheet = current_sheet

    try:
        confirm=(input('Delete timesheet "%s"? [y/N]: ' % sheet).strip().lower() == 'y')
    except(KeyboardInterrupt, EOFError):
        confirm=False

    if not confirm:
        print('cancelled')
        return None

    kill(db, sheet)
    if switch_to_default:
        commands.switch.switch(db, 'default')

def kill(db, sheet):
    """
    delete the specified sheet
    """
    db.execute('''
    delete from
        entry
    where sheet = ?;
    ''', (sheet,))

    db.execute('''
    delete from
        sheet_meta
    where sheet = ?;
    ''', (sheet,))

