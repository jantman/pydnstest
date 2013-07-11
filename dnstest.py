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
import optparse
import os.path
from dnstest_checks import DNStestChecks
from dnstest_config import DnstestConfig
from dnstest_parser import DnstestParser


config = None
parser = None
chk = None


def run_check_line(line):
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


def run_verify_line(line):
    """
    Parses a raw input line, runs the tests for that line verifying
    against the PROD server (i.e. once the changes have gone live)
    and returns the result of the tests.
    """
    d = parser.parse_line(line)
    if d['operation'] == 'add':
        return chk.verify_added_name(d['hostname'], d['value'])
    elif d['operation'] == 'remove':
        return chk.verify_removed_name(d['hostname'])
    elif d['operation'] == 'change':
        return chk.verify_changed_name(d['hostname'], d['value'])
    elif d['operation'] == 'rename':
        return chk.verify_renamed_name(d['hostname'], d['value'])
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
    for m in r['secondary']:
        print "\t%s" % m
    for w in r['warnings']:
        print "\t%s" % w


if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option('-c', '--config', dest='config_file',
                      help='path to config file (default looks for ./dnstest.ini or ~/.dnstest.ini)')

    parser.add_option('-f', '--file', dest='testfile',
                      help='path to file listing tests (default reads from STDIN)')

    parser.add_option('-V', '--verify', dest='verify', default=False, action='store_true',
                      help='verify changes against PROD server once they\'re live (default False)')

    options, args = parser.parse_args()

    # read in config, set variable
    config = DnstestConfig()
    if options.config_file:
        conf_file = options.config_file
    else:
        conf_file = config.find_config_file()
    if conf_file is None:
        print "ERROR: no configuration file."
        sys.exit(1)
    config.load_config(conf_file)

    parser = DnstestParser()
    chk = DNStestChecks(config)

    # if no other options, read from stdin
    if options.testfile:
        if not os.path.exists(options.testfile):
            print "ERROR: test file '%s' does not exist." % options.testfile
            sys.exit(1)
        fh = open(options.testfile, 'r')
    else:
        # read from stdin
        fh = sys.stdin

    # read input line by line, handle each line as we're given it
    for line in fh:
        line = line.strip()
        if not line:
            continue
        if line == "" or line[:1] == "#":
            continue
        if options.verify:
            r = run_verify_line(line)
        else:
            r = run_check_line(line)
        format_test_output(r)

    if options.testfile:
        # we were reading a file, close it
        fh.close()
