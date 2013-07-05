#!/usr/bin/env python
"""
Script to facilitate confirmation of DNS changes on a staging DNS server, comparing to prod.

Requirements:
- pydns from <http://pydns.sourceforge.net/>

See example_dns_test.py for usage - this should be called as a module from that script.

By Jason Antman <jason@jasonantman.com>

ToDo: flag to confirm against prod once live

"""

import dnstest_checks
import dnstest_config


config = {}


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
    conf_file = dnstest_config.find_config_file()
    if conf_file is None:
        sys.stderr.write("WARNING: no config file found. copy dnstest.conf.example to dnstest.conf or ~/.dnstest.conf.\n")
    else:
        config = dnstest_config.get_config(conf_file)

    # check command-line arguments, overwrite config
    print config
    print "not implemented yet"
