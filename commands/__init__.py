import os
import argparse
import re
import datetime
import time

from db import Database

# Create array of regex matches, prefixes and postfixes
today_str = time.strftime("%Y-%m-%d", datetime.datetime.now().timetuple())
matches = [(re.compile(r'^\d+:\d+$'), today_str + " ", ":00"),
           (re.compile(r'^\d+:\d+:\d+$'), today_str + " ", ""),
           (re.compile(r'^\d+-\d+-\d+$'), "", " 00:00:00"),
           (re.compile(r'^\d+-\d+-\d+\s+\d+:\d+$'), "", ":00"),
           (re.compile(r'^\d+-\d+-\d+\s+\d+:\d+:\d+$'), "", ""),
          ]
fmt = "%Y-%m-%d %H:%M:%S"

def parse_date_time(dt_str):
    """
    parse a date and time

    returns - time as an epoch integer
    """
    # iterate thru the array of matches
    for (patt, prepend, postpend) in matches:
        # if the regex matches
        if patt.match(dt_str):
            # return the time
            res = time.strptime(prepend + dt_str + postpend, fmt)
            return int(time.mktime(res))
    raise argparse.ArgumentTypeError('%s is not in a valid time format' % dt_str)

def parse_date_time_or_now(dt_str):
    """
    parse a date and time or return the current

    returns - time as an epoch integer
    """
    if dt_str:
        return parse_date_time(dt_str)
    else:
        return int(time.time())

def build_parser(**kwargs):
    """
    build a parser
    """
    parser=argparse.ArgumentParser(
        description='Parse a timebook command',
        formatter_class=argparse.RawTextHelpFormatter,
#         usage='%(prog)s [-h] [--config CONFIG] [--timebook TIMEBOOK] ' \
#            'COMMAND [ARGS...]',
        **kwargs)

    default_config=os.path.join(
        os.path.expanduser('~'),'.config','timebook3','timebook3.config')
    parser.add_argument('--config', '-c',
        dest='config',
        default=default_config,
        help='alternate configuration file (default: %s)' % default_config)

    default_timebook=os.path.join(
        os.path.expanduser('~'),'.config','timebook3','sheets.db')
    parser.add_argument('--timebook', '-b',
        dest='timebook',
        default=default_timebook,
        help='timebook database (default: %s)' % default_timebook)

    # load the commands
    subparsers = parser.add_subparsers(
        title='commands', metavar='COMMAND', help='a valid command')

    # load commands from file structure
    command_dir = __path__[0]
    modules=[f[:-3] for f in os.listdir(command_dir)
        if not f.startswith('_') and f.endswith('.py')]

    command_help=[]
    for module in sorted(modules):
        _module = __import__('commands.%s' % module, globals(), locals(),
            ['parser', 'command'], -1)
        command_help.append('%s - %s' % (module, _module.parser.description))
        subparser=subparsers.add_parser(module, parents=[_module.parser],
            aliases=getattr(_module, 'aliases', []))
        subparser.set_defaults(func=_module.command)

    subparsers.help='\n'.join(command_help)

    return parser

def execute_from_command_line(argv=None):
    """
    execute from command line
    """
    parser=build_parser()
    args=parser.parse_args(argv)
    args.func(**vars(args))

