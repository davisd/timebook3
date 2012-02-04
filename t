#!/usr/bin/env python
from commands import execute_from_command_line
import sys

if __name__ == "__main__":
    execute_from_command_line(sys.argv[1:] if len(sys.argv[1:]) else ['n'])

