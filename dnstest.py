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


def do_dns_tests(tests):
    """
    Run all DNS tests

    param tests: dict with keys 'added',
    """

    if 'added' in tests:
        check_added_names(tests['added'])
    if 'removed' in tests:
        check_removed_names(tests['removed'])
    if 'changed' in tests:
        check_changed_names(tests['changed'])
    return

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
        d = parser.parse_line(line)
        if d['operation'] == 'add':
            res = chk.check_added_name(d['hostname'], d['value'])

