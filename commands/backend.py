from sys import stdout, stderr
import os
import argparse
import subprocess
from db import Database
from config import parse_config

parser = argparse.ArgumentParser(add_help=False,
    description='Enter sqlite interactive shell with timebook db')

aliases=['b', 'shell']

def command(timebook, config, **kwargs):
    # get the db
    cfg=parse_config(config)
    db=Database(timebook, cfg)

    backend(timebook)

def backend(timebook):
    """
    execute the sqlite3 database backend with the db reference
    """
    subprocess.call(('sqlite3', timebook))

