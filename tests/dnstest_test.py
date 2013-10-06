# tests for main dnstest.py

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../')

from dnstest_checks import DNStestChecks
from dnstest_config import DnstestConfig
import dnstest
from dnstest_parser import DnstestParser

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
        dnstest.parser = parser

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
        dnstest.parser = parser

        chk = DNStestChecks(config)
        # stub
        chk.DNS.resolve_name = self.stub_resolve_name_verify
        # stub
        chk.DNS.lookup_reverse = self.stub_lookup_reverse_verify
        return (parser, chk)

    def stub_resolve_name(self, query, to_server, to_port=53):
        """
        DNS stub method

        return a dict that looks like the return value from dnstest.resolve_name
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

        return a dict that looks like the return value from dnstest.lookup_reverse
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

        return a dict that looks like the return value from dnstest.resolve_name
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

        return a dict that looks like the return value from dnstest.lookup_reverse
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
        chk, parser = setup_checks
        line = "foo bar baz"
        foo = dnstest.run_check_line(line, chk, parser)
        assert foo == False
        out, err = capfd.readouterr()
        assert out == "ERROR: could not parse input line, SKIPPING: %s\n" % line

    def test_parse_exception_verify(self, setup_checks, capfd):
        """
        Test parse exception on an input line.
        """
        chk, parser = setup_checks
        line = "foo bar baz"
        foo = dnstest.run_verify_line(line, chk, parser)
        assert foo == False
        out, err = capfd.readouterr()
        assert out == "ERROR: could not parse input line, SKIPPING: %s\n" % line

    @pytest.mark.parametrize(("line", "result"), [
            ("rename testrcl11.example.com with value 1.2.1.1 to testrcl12.example.com", {'message': 'rename testrcl11.example.com => testrcl12.example.com (TEST)', 'result': True, 'secondary': [], 'warnings': ['REVERSE NG: no reverse DNS appears to be set for 1.2.1.1 (TEST)']}),
            ("change testrcl2.example.com to 1.2.1.2", {'message': "change testrcl2.example.com from '1.2.1.3' to '1.2.1.2' (TEST)", 'result': True, 'secondary': [], 'warnings': ['REVERSE NG: no reverse DNS appears to be set for 1.2.1.2 (TEST)']}),
            ('add record testrcl3 address 1.2.1.3', {'message': 'testrcl3 => 1.2.1.3 (TEST)', 'result': True, 'secondary': ['PROD server returns NXDOMAIN for testrcl3 (PROD)'], 'warnings': ['REVERSE NG: got status NXDOMAIN for name 1.2.1.3 (TEST)']}),
            ('remove record testrcl4.example.com', {'message': 'testrcl4.example.com removed, got status NXDOMAIN (TEST)', 'result': True, 'warnings': [], 'secondary': ['PROD value was 1.2.1.4 (PROD)']}),
            ('confirm record testrcl5.example.com', {'message': "prod and test servers return same response for 'testrcl5.example.com'", 'result': True, 'warnings': [], 'secondary': ["response: {'typename': 'A', 'name': 'testrcl5.example.com', 'ttl': 360, 'type': 5, 'data': '1.2.1.5', 'class': 1, 'rdlength': 14, 'classstr': 'IN'}"]})
            ])
    def test_run_check_line(self, setup_checks, line, result):
        """
        Additional tests for the run_check_line function
        """
        chk, parser = setup_checks
        foo = dnstest.run_check_line(line, chk, parser)
        assert foo == result

    @pytest.mark.parametrize(("line", "result"), [
            ("rename testrvl11.example.com with value 1.2.1.1 to testrvl12.example.com", {'message': 'rename testrvl11.example.com => testrvl12.example.com (PROD)', 'result': True, 'secondary': [], 'warnings': ['REVERSE NG: no reverse DNS appears to be set for 1.2.1.1 (PROD)']}),
            ("change testrvl2.example.com to 1.2.1.2", {'message': "change testrvl2.example.com value to '1.2.1.2' (PROD)", 'result': True, 'secondary': [], 'warnings': ['REVERSE NG: no reverse DNS appears to be set for 1.2.1.2 (PROD)']}),
            ('add record testrvl3 address 1.2.1.3', {'message': 'testrvl3 => 1.2.1.3 (PROD)', 'result': True, 'secondary': [], 'warnings': ['REVERSE NG: got status NXDOMAIN for name 1.2.1.3 (PROD)']}),
            ('remove record testrvl4.example.com', {'message': 'testrvl4.example.com removed, got status NXDOMAIN (PROD)', 'result': True, 'warnings': [], 'secondary': []})
#            ('confirm record testrvl5.example.com', {'message': 'both test and prod returned status NXDOMAIN for name testrvl5.example.com', 'result': True, 'warnings': [], 'secondary': ["response: {'typename': 'A', 'name': 'testrvl5.example.com', 'ttl': 360, 'type': 5, 'data': '1.2.1.5', 'class': 1, 'rdlength': 14, 'classstr': 'IN'}"]})
            ])
    def test_run_verify_line(self, setup_verifies, line, result):
        """
        Additional tests for the run_verify_line function
        """
        chk, parser = setup_verifies
        foo = dnstest.run_verify_line(line, chk, parser)
        assert foo == result
