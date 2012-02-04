from sys import stdout, stderr
import os
import argparse
from datetime import timedelta
import time
from db import Database
from config import parse_config

from output import pprint_table

import locale
locale.setlocale( locale.LC_ALL, '' )

parser = argparse.ArgumentParser(add_help=False,
    description='List the available timesheets')

parser.add_argument('--simple', '-s', action='store_true', default=False,
    help='only display the names of the available timesheets')

aliases=['l', 'ls']

def command(timebook, config, simple, **kwargs):
    # get the db
    cfg=parse_config(config)
    db=Database(timebook, cfg)
    list(db, simple)

def list(db, simple):
    """
    list the available timesheets
    """
    if simple:
        db.execute(
        '''
        select
            distinct sheet
        from
            entry
        order by
            sheet asc;
        ''')
        print('\n'.join(r[0] for r in db.fetchall()))
        return

    table = [[' Timesheet', 'Running', 'Today', 'Total time', 'Rate', 'Billing Start']]
    db.execute('''
    select
        e1.sheet as name,
        e1.sheet = meta.value as is_current,
        ifnull((select
            strftime('%s', 'now') - e2.start_time
         from
            entry e2
         where
            e1.sheet = e2.sheet and e2.end_time is null), 0
        ) as active,
        (select
            ifnull(sum(ifnull(e3.end_time, strftime('%s', 'now')) -
                       e3.start_time), 0)
            from
                entry e3
            where
                e1.sheet = e3.sheet and
                e3.start_time > strftime('%s', date('now'))
        ) as today,
        ifnull(sum(ifnull(e1.end_time, strftime('%s', 'now')) -
                   e1.start_time), 0) as total,
        m.rate as rate,
        m.billing_start_time as billing_start_time
    from
        entry e1, meta
    left join
        sheet_meta m on m.sheet=e1.sheet
    where
        meta.key = 'current_sheet'
    group by e1.sheet
    order by e1.sheet asc;
    ''')
    sheets = db.fetchall()
    if len(sheets) == 0:
        print('(no sheets)')
        return
    for (name, is_current, active, today, total, rate, billing_start_time) in sheets:
        cur_name = '%s%s' % ('*' if is_current else ' ', name)
        active = str(timedelta(seconds=active)) if active != 0 \
                                                else '--'
        today = str(timedelta(seconds=today))
        total_time = str(timedelta(seconds=total))
        table.append([
            cur_name, active, today, total_time,
            locale.currency(rate/100) if rate else '--',
            time.strftime('%b %d, %Y %H:%M:%S',
                time.localtime(billing_start_time)) if billing_start_time else '--'
            ])
    pprint_table(table)

