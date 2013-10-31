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
from pyparsing import ParseException

from dnstest_checks import DNStestChecks
from dnstest_config import DnstestConfig
from dnstest_parser import DnstestParser

def run_check_line(line, parser, chk):
    """
    Parses a raw input line, runs the tests for that line,
    and returns the result of the tests.
    """
    try:
        d = parser.parse_line(line)
    except ParseException:
        print "ERROR: could not parse input line, SKIPPING: %s" % line
        return False

    if d['operation'] == 'add':
        return chk.check_added_name(d['hostname'], d['value'])
    elif d['operation'] == 'remove':
        return chk.check_removed_name(d['hostname'])
    elif d['operation'] == 'change':
        return chk.check_changed_name(d['hostname'], d['value'])
    elif d['operation'] == 'rename':
        return chk.check_renamed_name(d['hostname'], d['newname'], d['value'])
    elif d['operation'] == 'confirm':
        return chk.confirm_name(d['hostname'])
    else:
        print "ERROR: unknown input operation"
        return False


def run_verify_line(line, parser, chk):
    """
    Parses a raw input line, runs the tests for that line verifying
    against the PROD server (i.e. once the changes have gone live)
    and returns the result of the tests.
    """
    try:
        d = parser.parse_line(line)
    except ParseException:
        print "ERROR: could not parse input line, SKIPPING: %s" % line
        return False

    if d['operation'] == 'add':
        return chk.verify_added_name(d['hostname'], d['value'])
    elif d['operation'] == 'remove':
        return chk.verify_removed_name(d['hostname'])
    elif d['operation'] == 'change':
        return chk.verify_changed_name(d['hostname'], d['value'])
    elif d['operation'] == 'rename':
        return chk.verify_renamed_name(d['hostname'], d['newname'], d['value'])
    elif d['operation'] == 'confirm':
        return chk.confirm_name(d['hostname'])
    else:
        print "ERROR: unknown input operation"
        return False


def format_test_output(res):
    """
    Prints test output in a nice textual format
    """
    if res['result']:
        print "OK: %s" % res['message']
    else:
        print "**NG: %s" % res['message']
    for m in res['secondary']:
        print "\t%s" % m
    for w in res['warnings']:
        print "\t%s" % w

def main(options):
    """
    main function - does everything...

    split this out this way for testing...p
    """
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
    passed = 0
    failed = 0
    for line in fh:
        line = line.strip()
        if not line:
            continue
        if line[:1] == "#":
            continue
        if options.verify:
            r = run_verify_line(line, parser, chk)
        else:
            r = run_check_line(line, parser, chk)
        if r is False:
            continue
        elif r['result']:
            passed = passed + 1
        else:
            failed = failed + 1
        format_test_output(r)

    msg = ""
    if failed == 0:
        msg = "All %d tests passed." % passed
    else:
        msg = "%d passed / %d FAILED." % (passed, failed)
    print "++++ %s" % msg

    if options.testfile:
        # we were reading a file, close it
        fh.close()

def parse_opts():
    """
    Runs OptionParser and calls main() with the resulting options.
    """
    p = optparse.OptionParser()
    p.add_option('-c', '--config', dest='config_file',
                      help='path to config file (default looks for ./dnstest.ini or ~/.dnstest.ini)')

    p.add_option('-f', '--file', dest='testfile',
                      help='path to file listing tests (default reads from STDIN)')

    p.add_option('-V', '--verify', dest='verify', default=False, action='store_true',
                      help='verify changes against PROD server once they\'re live (default False)')

    options, args = p.parse_args()
    main(options)


if __name__ == "__main__":
    parse_opts()
