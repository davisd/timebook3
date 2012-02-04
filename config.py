import configparser
import os

def parse_config(filename):
    """
    parse the config file

    if the file does not exist, create it
    """
    config = configparser.SafeConfigParser()

    if not os.path.exists(filename):
        p=os.path.dirname(filename)
        if not os.path.exists(p):
            os.makedirs(p)
        f = open(filename, 'w')
        try:
            f.write('# timebook configuration file')
        finally:
            f.close()

    f = open(filename)
    try:
        config.readfp(f)
    finally:
        f.close()
    return config

