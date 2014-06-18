"""
pydnstest
Tool to test DNS changes on a staging DNS server, comparing to a current
production server, and verify changes after they go live.

See README.md for further information.

Requirements:
- pydns
- pyparsing

The latest version of this package is available at:
<https://github.com/jantman/pydnstest>

##################################################################################
Copyright 2013 Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>

    This file is part of pydnstest.

    pydnstest is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    pydnstest is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

The Copyright and Authors attributions contained herein may not be removed or
otherwise altered, except to add the Author attribution of a contributor to
this work. (Additional Terms pursuant to Section 7b of the AGPL v3)
##################################################################################
While not legally required, I sincerely request that anyone who finds
bugs please submit them at <https://github.com/jantman/pydnstest> or
to me via email, and that you send any contributions or improvements
either as a pull request on GitHub, or to me via email.
##################################################################################

AUTHORS:
Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>

"""

import sys
import optparse
import os.path
from pyparsing import ParseException
from time import sleep

from pydnstest.checks import DNStestChecks
from pydnstest.config import DnstestConfig
from pydnstest.parser import DnstestParser
from pydnstest.version import VERSION


def run_check_line(line, parser, chk):
    """
    Parses a raw input line, runs the tests for that line,
    and returns the result of the tests.
    """
    try:
        d = parser.parse_line(line)
    except ParseException:
        print("ERROR: could not parse input line, SKIPPING: %s" % line)
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
        print("ERROR: unknown input operation")
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
        print("ERROR: could not parse input line, SKIPPING: %s" % line)
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
        print("ERROR: unknown input operation")
        return False


def format_test_output(res):
    """
    Prints test output in a nice textual format
    """
    if res['result']:
        print("OK: %s" % res['message'])
    else:
        print("**NG: %s" % res['message'])
    for m in res['secondary']:
        print("\t%s" % m)
    for w in res['warnings']:
        print("\t%s" % w)


def main(options):
    """
    main function - does everything...

    split this out this way for testing...p
    """
    # read in config, set variable
    config = DnstestConfig()
    if options.exampleconf:
        config.set_example_values()
        print(config.to_string())
        raise SystemExit(0)

    if options.promptconfig:
        # interactively build a configuration file
        config.prompt_config()
        raise SystemExit(0)

    if options.config_file:
        conf_file = options.config_file
    else:
        conf_file = config.find_config_file()
    if conf_file is None:
        print("ERROR: no configuration file found. Run with --promptconfig to build one interactively, or --example-config for an example.")
        raise SystemExit(1)
    config.load_config(conf_file)

    if options.ignorettl:
        config.ignore_ttl = True

    if options.configprint:
        print("# {fname}".format(fname=config.conf_file))
        print(config.to_string())
        raise SystemExit(0)

    parser = DnstestParser()
    chk = DNStestChecks(config)

    if options.sleep:
        config.sleep = options.sleep
        print("Note - will sleep %g seconds between lines" % options.sleep)

    # if no other options, read from stdin
    if options.testfile:
        if not os.path.exists(options.testfile):
            print("ERROR: test file '%s' does not exist." % options.testfile)
            raise SystemExit(1)
        fh = open(options.testfile, 'r')
    else:
        # read from stdin
        sys.stderr.write("WARNING: reading from STDIN. Run with '-f filename' to read tests from a file.\n")
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
        if config.sleep is not None and config.sleep > 0.0:
            sleep(config.sleep)

    msg = ""
    if failed == 0:
        msg = "All %d tests passed. (pydnstest %s)" % (passed, VERSION)
    else:
        msg = "%d passed / %d FAILED. (pydnstest %s)" % (passed, failed, VERSION)
    print("++++ %s" % msg)

    if options.testfile:
        # we were reading a file, close it
        fh.close()


def parse_opts():
    """
    Runs OptionParser and calls main() with the resulting options.
    """
    usage = "%prog [-h|--help] [--version] [-c|--config path_to_config] [-f|--file path_to_test_file] [-V|--verify]"
    usage += "\n\npydnstest %s - <https://github.com/jantman/pydnstest/>" % VERSION
    usage += "\nlicensed under the GNU Affero General Public License - see LICENSE.txt"
    usage += "\nGrammar:\n\n"
    parser = DnstestParser()
    for s in parser.get_grammar():
        usage += "{s}\n".format(s=s)
    p = optparse.OptionParser(usage=usage, version="pydnstest %s" % VERSION)
    p.add_option('-c', '--config', dest='config_file',
                 help='path to config file (default looks for ./dnstest.ini or ~/.dnstest.ini)')

    p.add_option('-f', '--file', dest='testfile',
                 help='path to file listing tests (default reads from STDIN)')

    p.add_option('-V', '--verify', dest='verify', default=False, action='store_true',
                 help='verify changes against PROD server once they\'re live (default False)')

    p.add_option('-s', '--sleep', dest='sleep', action='store', type='float',
                 help='optionally, a decimal number of seconds to sleep between queries')

    p.add_option('-t', '--ignore-ttl', dest='ignorettl', default=False, action='store_true',
                 help='when comparing responses, ignore the TTL value')

    p.add_option('--example-config', dest='exampleconf', default=False, action='store_true',
                 help='print an example configuration file and exit')

    p.add_option('--configprint', dest='configprint', default=False, action='store_true',
                 help='print the current configuration and exit')

    p.add_option('--promptconfig', dest='promptconfig', default=False, action='store_true',
                 help='interactively build a configuration file through a series of prompts')

    options, args = p.parse_args()
    main(options)
