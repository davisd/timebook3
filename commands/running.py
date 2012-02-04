import argparse
from db import Database
from config import parse_config

from output import pprint_table

parser = argparse.ArgumentParser(add_help=False,
    description='Print all active sheets and any associated messages')

aliases=['r', 'active']

def command(timebook, config, **kwargs):
    # get the db
    cfg=parse_config(config)
    db=Database(timebook, cfg)

    running(db)

def running(db):
    """
    print all active sheets and any associated messages
    """
    db.execute('''
    select
        entry.sheet,
        case
            when entry.description = '' then '--'
            else entry.description
        end
    from
        entry
    where
        entry.end_time is null
    order by
        entry.sheet asc;
    ''')
    pprint_table([('Timesheet', 'Description')] + db.fetchall())

