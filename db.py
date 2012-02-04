import sqlite3

class Database(object):
    def __init__(self, path, config):
        """
        initialize the Database object

        path - sqlite database path
        config - parsed configuration
        """
        self.path = path
        self.config = config

        # connect to the db and get a cursor
        connection = sqlite3.connect(path, isolation_level=None)
        cursor = connection.cursor()

        # set shortcuts
        for attr in ('execute', 'executescript', 'fetchone', 'fetchall'):
            setattr(self, attr, getattr(cursor, attr))

        # initialize the db
        self._initialize_db()

    def _initialize_db(self):
        """
        initialize the database by creating tables and indexes if they 
        do not exist

        add the current_sheet key to meta if it is not there
        """
        self.executescript('''
        begin;
        create table if not exists meta (
            key varchar(16) primary key not null,
            value varchar(32) not null
        );
        create table if not exists entry (
            id integer primary key not null,
            sheet varchar(32) not null,
            start_time integer not null,
            end_time integer,
            description varchar(64) not null
        );
        create table if not exists sheet_meta(
            sheet varchar(32) primary key not null,
            billing_start_time integer,
            rate integer
        );
        create index if not exists entry_sheet on entry (sheet);
        create index if not exists entry_start_time on entry (start_time);
        create index if not exists entry_end_time on entry (end_time);

        create index if not exists sheet_meta_sheet on sheet_meta (sheet);
        create index if not exists sheet_meta_billing_start_time on 
            sheet_meta (billing_start_time);
        ''')

        self.execute('''
        select
            count(*)
        from
            meta
        where
            key = 'current_sheet'
        ''')
        count = self.fetchone()[0]
        if count < 1:
            self.execute('''
            insert into meta (
                key, value 
            ) values (
                'current_sheet', 'default'
            )''')

        self.execute('commit')

    def get_current_sheet(self):
        self.execute('''
        select
            value
        from
            meta
        where
            key = 'current_sheet'
        ''')
        return self.fetchone()[0]
    
    def get_sheet_names(self):
        self.execute('''
        select
            distinct sheet
        from
            entry
        ''')
        return tuple(r[0] for r in self.fetchall())
    
    def get_active_info(self, sheet):
        self.execute('''
        select
            strftime('%s', 'now') - entry.start_time,
            entry.description
        from
            entry
        where
            entry.sheet = ? and
            entry.end_time is null
        ''', (sheet,))
        return self.fetchone()
    
    def get_current_active_info(self):
        self.execute('''
        select
            entry.id,
            strftime('%s', 'now') - entry.start_time
        from
            entry
        inner join
            meta
        on
            meta.key = 'current_sheet' and
            meta.value = entry.sheet
        where
            entry.end_time is null
        ''')
        return self.fetchone()
    
    def get_current_start_time(self):
        self.execute('''
        select
            entry.id,
            entry.start_time
        from
            entry
        inner join
            meta
        on
            meta.key = 'current_sheet' and
            meta.value = entry.sheet
        where
            entry.end_time is null
        ''')
        return self.fetchone()

    def get_start_time(self, sheet):
        self.execute('''
        select
            id,
            start_time
        from
            entry
        where
            sheet = ?
            and entry.end_time is null
        ''', (sheet,))
        return self.fetchone()
    
    def get_entry_count(self, sheet):
        self.execute('''
        select
            count(*)
        from
            entry e
        where
            sheet = ?
        ''', (sheet,))
        return self.fetchone()[0]
    
    def get_most_recent_clockout(self, sheet):
        self.execute('''
        select
            end_time, description
        from
            entry
        where
            sheet = ?
        order by
            -end_time
        ''', (sheet,))
        return self.fetchone()

    def get_billing_start_time(self, sheet):
        self.execute('''
        select
            billing_start_time
        from
            sheet_meta
        where
            sheet = ?
        ''', (sheet,))
        bt=self.fetchone()
        return bt[0] if bt else None

    def get_rate(self, sheet):
        self.execute('''
        select
            rate
        from
            sheet_meta
        where
            sheet = ?
        ''', (sheet,))
        bt=self.fetchone()
        return bt[0] if bt else None

    def get_entries(self, sheet, start, end):
        self.execute('''
        select
            e.id
            e.start_time,
            e.end_time,
            e.descripton
        from
            entry e
        where
            sheet = ?
            and (e.start_time >= ? or ? = '')
            and (e.end_time < ? or ? = '')
        ''', (sheet,
            start or '', start or '',
            end or '', end or ''))
        return self.fetchall()

