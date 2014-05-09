"""
pydnstest
tests for main dnstest.py script

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

import pytest
import sys
import os

from pydnstest.checks import DNStestChecks
from pydnstest.config import DnstestConfig
import pydnstest.main
from pydnstest.parser import DnstestParser

"""
This dict stores the DNS results that our DNS-mocking functions will return.
Format of the 'known_dns' dict:
[chk|ver] - whether this is pre-change (_check methods) or post-change (_verify methods)
    [prod|test] - whether this is for the prod or test DNS server
        [fwd|rev] - whether this is forward or reverse DNS
            [recordname] - the name of this record, as sent to the DNS query methods
                = value - a string or list of the record value, see below
value can be:
for 'rev' dns:
  - a string with the value of the PTR record
  - the string "SERVFAIL", which returns a SERVFAIL result
for 'fwd' dns:
  - a list whose first item is "STATUS", and whose second item is the 'status' attribute of the DNS result
  - a list whose first item is the data/value of the record, and whose second item is the typename of the record (i.e. "A" or "CNAME")
"""
known_dns = {'chk': {'test': {'fwd': {}, 'rev': {}}, 'prod': {'fwd': {}, 'rev': {}}}, 'ver': {'test': {'fwd': {}, 'rev': {}}, 'prod': {'fwd': {}, 'rev': {}}}}

# test_run_check_line
# 1
known_dns['chk']['test']['fwd']['testrcl12.example.com'] = ['1.2.1.1', 'A']
known_dns['chk']['prod']['fwd']['testrcl11.example.com'] = ['1.2.1.1', 'A']

# 2
known_dns['chk']['test']['fwd']['testrcl2.example.com'] = ['1.2.1.2', 'A']
known_dns['chk']['prod']['fwd']['testrcl2.example.com'] = ['1.2.1.3', 'A']

# 3
known_dns['chk']['test']['fwd']['testrcl3.example.com'] = ['1.2.1.3', 'A']

# 4
known_dns['chk']['prod']['fwd']['testrcl4.example.com'] = ['1.2.1.4', 'A']

# 5
known_dns['chk']['prod']['fwd']['testrcl5.example.com'] = ['1.2.1.5', 'A']
known_dns['chk']['test']['fwd']['testrcl5.example.com'] = ['1.2.1.5', 'A']

# 6
known_dns['chk']['prod']['fwd']['m.example.com'] = ['1.2.1.6', 'A']
known_dns['chk']['test']['fwd']['m.example.com'] = ['1.2.1.6', 'A']

# 7
known_dns['chk']['test']['fwd']['_discover.example.com'] = ['1.2.1.7', 'A']

# 8
known_dns['chk']['test']['fwd']['foobar._discover.example.com'] = ['1.2.1.8', 'A']

# test_run_verify_line
# 1
known_dns['ver']['test']['fwd']['testrvl12.example.com'] = ['1.2.1.1', 'A']
known_dns['ver']['prod']['fwd']['testrvl12.example.com'] = ['1.2.1.1', 'A']

# 2
known_dns['ver']['test']['fwd']['testrvl2.example.com'] = ['1.2.1.2', 'A']
known_dns['ver']['prod']['fwd']['testrvl2.example.com'] = ['1.2.1.2', 'A']

# 3
known_dns['ver']['test']['fwd']['testrvl3.example.com'] = ['1.2.1.3', 'A']
known_dns['ver']['prod']['fwd']['testrvl3.example.com'] = ['1.2.1.3', 'A']

# 4

# 5
known_dns['ver']['prod']['fwd']['testrvl5.example.com'] = ['1.2.1.5', 'A']
known_dns['ver']['test']['fwd']['testrvl5.example.com'] = ['1.2.1.5', 'A']

# 6
known_dns['ver']['prod']['fwd']['m.example.com'] = ['1.2.1.6', 'A']
known_dns['ver']['test']['fwd']['m.example.com'] = ['1.2.1.6', 'A']

# 7
known_dns['ver']['prod']['fwd']['_discover.example.com'] = ['1.2.1.7', 'A']
known_dns['ver']['test']['fwd']['_discover.example.com'] = ['1.2.1.7', 'A']

# 8
known_dns['ver']['prod']['fwd']['foobar._discover.example.com'] = ['1.2.1.8', 'A']
known_dns['ver']['test']['fwd']['foobar._discover.example.com'] = ['1.2.1.8', 'A']


class TestDNSTest:
    """
    Tests the main dnstest.py script
    """

    @pytest.fixture(scope="module")
    def setup_checks(self):
        """
        Sets up test environment for tests of check methods,
        including redefining resolve_name and lookup_reverse
        to the appropriate methods in this class
        """
        config = DnstestConfig()
        config.server_test = "test"
        config.server_prod = "prod"
        config.default_domain = ".example.com"
        config.have_reverse_dns = True

        parser = DnstestParser()
        pydnstest.parser = parser

        chk = DNStestChecks(config)
        # stub
        chk.DNS.resolve_name = self.stub_resolve_name
        # stub
        chk.DNS.lookup_reverse = self.stub_lookup_reverse
        return (parser, chk)

    @pytest.fixture(scope="module")
    def setup_verifies(self):
        """
        Sets up test environment for tests of verify methods,
        including redefining resolve_name and lookup_reverse
        to the appropriate methods in this class
        """
        config = DnstestConfig()
        config.server_test = "test"
        config.server_prod = "prod"
        config.default_domain = ".example.com"
        config.have_reverse_dns = True

        parser = DnstestParser()
        pydnstest.parser = parser

        chk = DNStestChecks(config)
        # stub
        chk.DNS.resolve_name = self.stub_resolve_name_verify
        # stub
        chk.DNS.lookup_reverse = self.stub_lookup_reverse_verify
        return (parser, chk)

    def stub_resolve_name(self, query, to_server, to_port=53):
        """
        DNS stub method

        return a dict that looks like the return value from pydnstest.resolve_name
        but either returns one of a hard-coded group of dicts, or an error.
        """

        if query in known_dns['chk'][to_server]['fwd'] and known_dns['chk'][to_server]['fwd'][query][0] == "STATUS":
            return {'status': known_dns['chk'][to_server]['fwd'][query][1]}
        elif query in known_dns['chk'][to_server]['fwd']:
            return {'answer': {'name': query, 'data': known_dns['chk'][to_server]['fwd'][query][0], 'typename': known_dns['chk'][to_server]['fwd'][query][1], 'classstr': 'IN', 'ttl': 360, 'type': 5, 'class': 1, 'rdlength': 14}}
        else:
            return {'status': 'NXDOMAIN'}

    def stub_lookup_reverse(self, name, to_server, to_port=53):
        """
        DNS stub method

        return a dict that looks like the return value from pydnstest.lookup_reverse
        but either returns one of a hard-coded group of dicts, or an error.
        """

        if name in known_dns['chk'][to_server]['rev'] and known_dns['chk'][to_server]['rev'][name] == "SERVFAIL":
            return {'status': 'SERVFAIL'}
        elif name in known_dns['chk'][to_server]['rev']:
            return {'answer': {'name': name, 'data': known_dns['chk'][to_server]['rev'][name], 'typename': 'PTR', 'classstr': 'IN', 'ttl': 360, 'type': 12, 'class': 1, 'rdlength': 33}}
        else:
            return {'status': 'NXDOMAIN'}

    def stub_resolve_name_verify(self, query, to_server, to_port=53):
        """
        DNS stub method

        return a dict that looks like the return value from pydnstest.resolve_name
        but either returns one of a hard-coded group of dicts, or an error.
        """

        if query in known_dns['ver'][to_server]['fwd'] and known_dns['ver'][to_server]['fwd'][query][0] == "STATUS":
            return {'status': known_dns['ver'][to_server]['fwd'][query][1]}
        elif query in known_dns['ver'][to_server]['fwd']:
            return {'answer': {'name': query, 'data': known_dns['ver'][to_server]['fwd'][query][0], 'typename': known_dns['ver'][to_server]['fwd'][query][1], 'classstr': 'IN', 'ttl': 360, 'type': 5, 'class': 1, 'rdlength': 14}}
        else:
            return {'status': 'NXDOMAIN'}

    def stub_lookup_reverse_verify(self, name, to_server, to_port=53):
        """
        DNS stub method

        return a dict that looks like the return value from pydnstest.lookup_reverse
        but either returns one of a hard-coded group of dicts, or an error.
        """

        if name in known_dns['ver'][to_server]['rev'] and known_dns['ver'][to_server]['rev'][name] == "SERVFAIL":
            return {'status': 'SERVFAIL'}
        elif name in known_dns['ver'][to_server]['rev']:
            return {'answer': {'name': name, 'data': known_dns['ver'][to_server]['rev'][name], 'typename': 'PTR', 'classstr': 'IN', 'ttl': 360, 'type': 12, 'class': 1, 'rdlength': 33}}
        else:
            return {'status': 'NXDOMAIN'}

    ###########################################
    # Done with setup, start the actual tests #
    ###########################################

    def test_parse_exception_check(self, setup_checks, capfd):
        """
        Test parse exception on an input line.
        """
        parser, chk = setup_checks
        line = "foo bar baz"
        foo = pydnstest.main.run_check_line(line, parser, chk)
        assert foo == False
        out, err = capfd.readouterr()
        assert out == "ERROR: could not parse input line, SKIPPING: %s\n" % line

    def test_parse_exception_verify(self, setup_checks, capfd):
        """
        Test parse exception on an input line.
        """
        parser, chk = setup_checks
        line = "foo bar baz"
        foo = pydnstest.main.run_verify_line(line, parser, chk)
        assert foo == False
        out, err = capfd.readouterr()
        assert out == "ERROR: could not parse input line, SKIPPING: %s\n" % line

    @pytest.mark.parametrize(("line", "result"), [
        ("rename testrcl11.example.com with value 1.2.1.1 to testrcl12.example.com", {'message': 'rename testrcl11.example.com => testrcl12.example.com (TEST)', 'result': True, 'secondary': [], 'warnings': ['REVERSE NG: no reverse DNS appears to be set for 1.2.1.1 (TEST)']}),
        ("change testrcl2.example.com to 1.2.1.2", {'message': "change testrcl2.example.com from '1.2.1.3' to '1.2.1.2' (TEST)", 'result': True, 'secondary': [], 'warnings': ['REVERSE NG: no reverse DNS appears to be set for 1.2.1.2 (TEST)']}),
        ('add record testrcl3 address 1.2.1.3', {'message': 'testrcl3 => 1.2.1.3 (TEST)', 'result': True, 'secondary': ['PROD server returns NXDOMAIN for testrcl3 (PROD)'], 'warnings': ['REVERSE NG: got status NXDOMAIN for name 1.2.1.3 (TEST)']}),
        ('remove record testrcl4.example.com', {'message': 'testrcl4.example.com removed, got status NXDOMAIN (TEST)', 'result': True, 'warnings': [], 'secondary': ['PROD value was 1.2.1.4 (PROD)']}),
        ('confirm record testrcl5.example.com', {'message': "prod and test servers return same response for 'testrcl5.example.com'", 'result': True, 'warnings': [], 'secondary': ["response: {'class': 1, 'classstr': 'IN', 'data': '1.2.1.5', 'name': 'testrcl5.example.com', 'rdlength': 14, 'ttl': 360, 'type': 5, 'typename': 'A'}"]}),
        ('confirm record m.example.com', {'message': "prod and test servers return same response for 'm.example.com'", 'result': True, 'warnings': [], 'secondary': ["response: {'class': 1, 'classstr': 'IN', 'data': '1.2.1.6', 'name': 'm.example.com', 'rdlength': 14, 'ttl': 360, 'type': 5, 'typename': 'A'}"]}),
        ('add record _discover.example.com address 1.2.1.7', {'message': '_discover.example.com => 1.2.1.7 (TEST)', 'result': True, 'secondary': ['PROD server returns NXDOMAIN for _discover.example.com (PROD)'], 'warnings': ['REVERSE NG: got status NXDOMAIN for name 1.2.1.7 (TEST)']}),
        ('add record foobar._discover.example.com address 1.2.1.8', {'message': 'foobar._discover.example.com => 1.2.1.8 (TEST)', 'result': True, 'secondary': ['PROD server returns NXDOMAIN for foobar._discover.example.com (PROD)'], 'warnings': ['REVERSE NG: got status NXDOMAIN for name 1.2.1.8 (TEST)']})
    ])
    def test_run_check_line(self, setup_checks, line, result):
        """
        Additional tests for the run_check_line function
        """
        parser, chk = setup_checks
        foo = pydnstest.main.run_check_line(line, parser, chk)
        assert foo == result

    @pytest.mark.parametrize(("line", "result"), [
        ("rename testrvl11.example.com with value 1.2.1.1 to testrvl12.example.com", {'message': 'rename testrvl11.example.com => testrvl12.example.com (PROD)', 'result': True, 'secondary': [], 'warnings': ['REVERSE NG: no reverse DNS appears to be set for 1.2.1.1 (PROD)']}),
        ("change testrvl2.example.com to 1.2.1.2", {'message': "change testrvl2.example.com value to '1.2.1.2' (PROD)", 'result': True, 'secondary': [], 'warnings': ['REVERSE NG: no reverse DNS appears to be set for 1.2.1.2 (PROD)']}),
        ('add record testrvl3 address 1.2.1.3', {'message': 'testrvl3 => 1.2.1.3 (PROD)', 'result': True, 'secondary': [], 'warnings': ['REVERSE NG: got status NXDOMAIN for name 1.2.1.3 (PROD)']}),
        ('remove record testrvl4.example.com', {'message': 'testrvl4.example.com removed, got status NXDOMAIN (PROD)', 'result': True, 'warnings': [], 'secondary': []}),
        ('confirm record testrvl5.example.com', {'message': "prod and test servers return same response for 'testrvl5.example.com'", 'result': True, 'warnings': [], 'secondary': ["response: {'class': 1, 'classstr': 'IN', 'data': '1.2.1.5', 'name': 'testrvl5.example.com', 'rdlength': 14, 'ttl': 360, 'type': 5, 'typename': 'A'}"]}),
        ('confirm record m.example.com', {'message': "prod and test servers return same response for 'm.example.com'", 'result': True, 'warnings': [], 'secondary': ["response: {'class': 1, 'classstr': 'IN', 'data': '1.2.1.6', 'name': 'm.example.com', 'rdlength': 14, 'ttl': 360, 'type': 5, 'typename': 'A'}"]}),
        ('add record _discover.example.com address 1.2.1.7', {'message': '_discover.example.com => 1.2.1.7 (PROD)', 'result': True, 'secondary': [], 'warnings': ['REVERSE NG: got status NXDOMAIN for name 1.2.1.7 (PROD)']}),
        ('add record foobar._discover.example.com address 1.2.1.8', {'message': 'foobar._discover.example.com => 1.2.1.8 (PROD)', 'result': True, 'secondary': [], 'warnings': ['REVERSE NG: got status NXDOMAIN for name 1.2.1.8 (PROD)']})
    ])
    def test_run_verify_line(self, setup_verifies, line, result):
        """
        Additional tests for the run_verify_line function
        """
        parser, chk = setup_verifies
        foo = pydnstest.main.run_verify_line(line, parser, chk)
        assert foo == result

    @pytest.fixture(scope="module")
    def setup_parser_return_unknown_op(self):
        """
        Sets up test environment for tests of check methods,
        including redefining resolve_name and lookup_reverse
        to the appropriate methods in this class
        """
        config = DnstestConfig()
        config.server_test = "test"
        config.server_prod = "prod"
        config.default_domain = ".example.com"
        config.have_reverse_dns = True

        parser = DnstestParser()
        # mock the parser function to just return None
        parser.parse_line = self.parser_return_unknown_op
        pydnstest.parser = parser

        chk = DNStestChecks(config)
        # stub
        chk.DNS.resolve_name = self.stub_resolve_name
        # stub
        chk.DNS.lookup_reverse = self.stub_lookup_reverse
        return (parser, chk)

    def parser_return_unknown_op(self, line):
        """
        Returns unknown operation
        """
        return {'operation': 'unknown'}

    def test_check_parser_false(self, setup_parser_return_unknown_op, capfd):
        """
        Test (unreachable) parser return None.
        """
        parser, chk = setup_parser_return_unknown_op

        foo = pydnstest.main.run_check_line("confirm foo.example.com", parser, chk)
        assert foo == False
        out, err = capfd.readouterr()
        assert out == "ERROR: unknown input operation\n"

    def test_verify_parser_false(self, setup_parser_return_unknown_op, capfd):
        """
        Test (unreachable) parser return None.
        """
        parser, chk = setup_parser_return_unknown_op

        foo = pydnstest.main.run_verify_line("confirm foo.example.com", parser, chk)
        assert foo == False
        out, err = capfd.readouterr()
        assert out == "ERROR: unknown input operation\n"

    @pytest.mark.parametrize(("result", "output"), [
        ({'message': 'cnametestonly => foobar (PROD)', 'result': True, 'secondary': [], 'warnings': []}, "OK: cnametestonly => foobar (PROD)\n"),
        ({'message': 'cnametestonly => foobar (TEST)', 'result': True, 'secondary': ['PROD server returns NXDOMAIN for cnametestonly (PROD)'], 'warnings': []}, "OK: cnametestonly => foobar (TEST)\n\tPROD server returns NXDOMAIN for cnametestonly (PROD)\n"),
        ({'message': 'rename testrvl11.example.com => testrvl12.example.com (PROD)', 'result': True, 'secondary': [], 'warnings': ['REVERSE NG: no reverse DNS appears to be set for 1.2.1.1 (PROD)']}, "OK: rename testrvl11.example.com => testrvl12.example.com (PROD)\n\tREVERSE NG: no reverse DNS appears to be set for 1.2.1.1 (PROD)\n"),
        ({'message': 'newhostname => 1.2.3.1 (TEST)', 'result': True, 'secondary': ['PROD server returns NXDOMAIN for newhostname (PROD)'], 'warnings': ['REVERSE NG: got status NXDOMAIN for name 1.2.3.1 (TEST)']}, "OK: newhostname => 1.2.3.1 (TEST)\n\tPROD server returns NXDOMAIN for newhostname (PROD)\n\tREVERSE NG: got status NXDOMAIN for name 1.2.3.1 (TEST)\n"),
        ({'message': 'new name existinghostname returned valid result from prod server (PROD)', 'result': False, 'secondary': [], 'warnings': []}, "**NG: new name existinghostname returned valid result from prod server (PROD)\n"),
        ({'message': 'addtest4 resolves to 1.2.3.1 instead of 1.2.3.5 (TEST)', 'result': False, 'secondary': ['PROD server returns NXDOMAIN for addtest4 (PROD)'], 'warnings': ['REVERSE NG: got status NXDOMAIN for name 1.2.3.5 (TEST)']}, "**NG: addtest4 resolves to 1.2.3.1 instead of 1.2.3.5 (TEST)\n\tPROD server returns NXDOMAIN for addtest4 (PROD)\n\tREVERSE NG: got status NXDOMAIN for name 1.2.3.5 (TEST)\n"),
        ({'message': 'addtest4 resolves to 1.2.3.13 instead of 1.2.3.5 (PROD)', 'result': False, 'secondary': [], 'warnings': ['REVERSE NG: got status NXDOMAIN for name 1.2.3.5 (PROD)']}, "**NG: addtest4 resolves to 1.2.3.13 instead of 1.2.3.5 (PROD)\n\tREVERSE NG: got status NXDOMAIN for name 1.2.3.5 (PROD)\n"),
    ])
    def test_format_test_output(self, setup_checks, capfd, result, output):
        """
        Test output formatting of test results.
        """
        parser, chk = setup_checks
        foo = pydnstest.main.format_test_output(result)
        out, err = capfd.readouterr()
        assert out == output
