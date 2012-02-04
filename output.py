import time
from datetime import datetime, timedelta
from sys import stdout
import locale

locale.setlocale( locale.LC_ALL, '' )

def timedelta_hms_display(timedelta):
    hours = timedelta.days * 24 + timedelta.seconds / 3600
    minutes = timedelta.seconds / 60 % 60
    seconds = timedelta.seconds % 60
    return '%02d:%02d:%02d' % (hours, minutes, seconds)
displ_date = lambda t: time.strftime('%b %d, %Y', time.localtime(t))
displ_time = lambda t: time.strftime('%H:%M:%S', time.localtime(t))
displ_total = lambda t: timedelta_hms_display(timedelta(seconds=t))
displ_amount = lambda t, r: '--' if not r else locale.currency(
    ((r/100)*(t/60/60)), grouping=True)

def pprint_table(table):
    """
    print a padded table
    """
    widths = [3 + max(len(row[col]) for row in table) for col
        in range(len(table[0]))]
    for row in table:
        # Don't pad the final column
        first_cols = [cell + ' ' * (spacing - len(cell))
            for (cell, spacing) in zip(row[:-1], widths[:-1])]
        print(''.join(first_cols + [row[-1]]))

def format_timebook(db, sheet, start_timestamp, end_timestamp, money):
    """
    output timebook format
    """
    db.execute('''
    select count(*)
    from
        entry
    where
        sheet = ?
        and (? is null or start_time >= ?)
        and (? is null or end_time < ?)
    ''', (sheet,
        start_timestamp, start_timestamp,
        end_timestamp, end_timestamp))

    if db.fetchone()[0] < 1:
        print('(empty)')
        return

    last_day = None
    table = [['Day', 'Start      End', 'Duration', 'Notes']]
    if money:
        table[0].append('Money')

    db.execute('''
    select
        ifnull(sum(ifnull(e.end_time, strftime('%s', 'now')) -
                   e.start_time), 0) as total,
        m.rate as rate
    from
        entry e
    left join
        sheet_meta as m
    on
       e.sheet = m.sheet
    where
        e.sheet = ?
        and (? is null or e.start_time >= ?)
        and (? is null or e.end_time < ?)
    ''', (sheet,
        start_timestamp, start_timestamp,
        end_timestamp, end_timestamp))
    total, rate = db.fetchone()

    db.execute('''
    select
        date(e.start_time, 'unixepoch', 'localtime') as day,
        ifnull(sum(ifnull(e.end_time, strftime('%s', 'now')) -
            e.start_time), 0) as day_total
    from
        entry e
    where
        e.sheet = ?
        and (? is null or e.start_time >= ?)
        and (? is null or e.end_time < ?)
    group by
        day
    order by
        day asc;
    ''', (sheet,
        start_timestamp, start_timestamp,
        end_timestamp, end_timestamp))
    days = db.fetchall()
    days_iter = iter(days)
    db.execute('''
    select
        date(e.start_time, 'unixepoch', 'localtime') as day,
        e.start_time as start,
        e.end_time as end,
        ifnull(e.end_time, strftime('%s', 'now')) - e.start_time as
            duration,
        case
            when e.description = '' then '--'
            else e.description
        end as description,
        m.rate as rate
    from
        entry e
    left join
        sheet_meta m on m.sheet = e.sheet
    where
        e.sheet = ?
        and (? is null or e.start_time >= ?)
        and (? is null or e.end_time < ?)
    order by
        day asc;
    ''', (sheet,
        start_timestamp, start_timestamp,
        end_timestamp, end_timestamp))
    entries = db.fetchall()

    for i, (day, start, end, duration, description, rate) in \
            enumerate(entries):
        date = displ_date(start)
        diff = displ_total(duration)
        if end is None:
            trange = '%s -' % displ_time(start)
        else:
            trange = '%s - %s' % (displ_time(start), displ_time(end))
        if last_day == day:
            # If this row doesn't represent the first entry of the
            # day, don't display anything in the day column.
            r=['', trange, diff, description, ]
            if money:
                r.append(displ_amount(duration, rate))
            table.append(r)
        else:
            if last_day is not None:
                # Use day_total set (below) from the previous
                # iteration. This is skipped the first iteration,
                # since last_day is None.
                r = ['', '', displ_total(day_total), '',]
                if money:
                    r.append(displ_amount(day_total, rate))
                table.append(r)
            cur_day, day_total = days_iter.__next__()
            assert day == cur_day
            r = [date, trange, diff, description]
            if money:
                r.append(displ_amount(duration, rate))
            table.append(r)
            last_day = day

    r1=['', '', displ_total(day_total), '']
    r2=['Total', '', displ_total(total),
        '$%.2f/hr' % (rate/100) if money and rate else '']
    if money:
        r1.append(displ_amount(day_total, rate))
        r2.append(displ_amount(total, rate))

    table.append(r1)
    table.append(r2)

    pprint_table(table)

def format_csv(db, sheet, start_timestamp, end_timestamp):
    import csv

    writer = csv.writer(stdout)
    writer.writerow(('Start', 'End', 'Length', 'Description'))
    db.execute('''
    select
       start_time,
       end_time,
       ifnull(end_time, strftime('%s', 'now')) -
           start_time,
    case
        when description = '' then '--'
        else description
    end as description
    from
       entry
    where
        sheet = ?
        and (? is null or start_time >= ?)
        and (? is null or end_time < ?)
        -- No null values for csv output
        and end_time is not null
    ''', (sheet,
        start_timestamp, start_timestamp,
        end_timestamp, end_timestamp))
    format = lambda t: datetime.fromtimestamp(t).strftime(
        '%m/%d/%Y %H:%M:%S')
    rows = db.fetchall()
    writer.writerows(map(lambda row: (
        format(row[0]), format(row[1]), row[2], row[3]), rows))
    total_formula = '=SUM(C2:C%d)/3600' % (len(rows) + 1)
    writer.writerow(('Total', '', total_formula, ''))

def format_report(db, start_timestamp, end_timestamp,
        billing=False, money=False):
    table = []
    r=['Sheet', 'Total']
    if money:
        r.append('Money')
    table.append(r)

    db.execute('''
    select
        e.sheet,
        sum(ifnull(e.end_time, strftime('%s', 'now')) - e.start_time)
            as duration,
        m.rate
    from
        entry e
    left join
        sheet_meta m on e.sheet = m.sheet
    where
        (? is null or e.start_time >= ?)
        and (? is null or e.end_time < ?)
        and (? = 0 or m.billing_start_time is null
            or e.start_time >= m.billing_start_time)
    group by
        e.sheet
    order by
        e.sheet asc
    ''', (start_timestamp, start_timestamp,
        end_timestamp, end_timestamp,
        billing))
    sheets = db.fetchall()
    total = 0
    total_amount = 0
    for (sheet, duration, rate) in sheets:
        total += duration

        if rate != None and total_amount != None:
            total_amount+=((rate/100)*(duration/60/60))
        else:
            total_amount = None

        r=[sheet, displ_total(duration)]
        if money:
            r.append(displ_amount(duration, rate))
        table.append(r)

    r=['Total', displ_total(total)]
    if money:
        r.append('--' if not total_amount else \
            locale.currency(total_amount, grouping=True))
    table.append(r)

    pprint_table(table)

