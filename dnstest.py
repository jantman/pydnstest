#!/usr/bin/env python
"""
Script to facilitate confirmation of DNS changes on a staging DNS server, comparing to prod.

Requirements:
- pydns from <http://pydns.sourceforge.net/>

See example_dns_test.py for usage - this should be called as a module from that script.

By Jason Antman <jason@jasonantman.com>

ToDo: flag to confirm against prod once live

"""

import sys
from dnstest_checks import DNStestChecks
from dnstest_config import DnstestConfig
from dnstest_parser import DnstestParser


config = None
parser = None
chk = None


def run_input_line(line):
    """
    Parses a raw input line, runs the tests for that line,
    and returns the result of the tests.
    """
    d = parser.parse_line(line)
    if d['operation'] == 'add':
        return chk.check_added_name(d['hostname'], d['value'])
    elif d['operation'] == 'remove':
        return chk.check_removed_name(d['hostname'])
    elif d['operation'] == 'change':
        return chk.check_changed_name(d['hostname'], d['value'])
    elif d['operation'] == 'rename':
        return chk.check_renamed_name(d['hostname'], d['value'])
    else:
        print "ERROR: unknown input operation"
        return False


def format_test_output(res):
    """
    Prints test output in a nice textual format
    """
    if r['result']:
        print "OK: %s" % r['message']
    else:
        print "**NG: %s" % r['message']
    # @TODO: print warnings and secondary messages


if __name__ == "__main__":
    # read in config, set variable
    config = DnstestConfig()
    conf_file = config.find_config_file()
    if conf_file is None:
        print "ERROR: no configuration file."
        sys.exit(1)
    config.load_config(conf_file)

    parser = DnstestParser()
    chk = DNStestChecks(config)

    # if no other options, read from stdin
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        if line == "" or line[:1] == "#":
            continue
        r = run_input_line(line)
        format_test_output(r)
