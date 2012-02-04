from sys import stdout, stderr
import os
import argparse
import subprocess
from db import Database
from config import parse_config

parser = argparse.ArgumentParser(add_help=False,
    description='Switch sheets')

parser.add_argument('sheet',
    help='timebook sheet')

aliases=['s']

def command(timebook, config, sheet, **kwargs):
    # get the db
    cfg=parse_config(config)
    db=Database(timebook, cfg)

    switch(db, sheet)

def switch(db, sheet):
    """
    switch the sheet
    """
    if db.get_current_sheet() != sheet:
        db.execute('''
        update
            meta
        set
            value = ?
        where
            key = 'current_sheet'
        ''', (sheet,))

