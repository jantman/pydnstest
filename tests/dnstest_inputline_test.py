# tests for dns_parser.py

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../')

from dnstest_checks import DNStestChecks
from dnstest_config import DnstestConfig
import dnstest
from dnstest_parser import DnstestParser


# dict of known (mocked) reverse DNS values for test and prod servers
known_rev_dns = {'test_server_stub': {}, 'prod_server_stub': {}}
known_rev_dns['test_server_stub']['10.188.12.10'] = 'foo.example.com'

# dict of known (mocked) forward DNS values for test and prod servers
# each known_dns[server][name] is [value, record_type]
known_dns = {'test_server_stub': {}, 'prod_server_stub': {}}
known_dns['test_server_stub']['newhostname.example.com'] = ['1.2.3.1', 'A']
known_dns['prod_server_stub']['existinghostname.example.com'] = ['1.2.3.2', 'A']
known_dns['test_server_stub']['addedhostname.example.com'] = ['1.2.3.3', 'A']
known_dns['prod_server_stub']['addedhostname.example.com'] = ['1.2.3.3', 'A']


class TestDNSChecks:
    """
    Test DNS checks, using stubbed name resolution methods that return static values.

    The code in this class checks the logic of dnstest.py's test_*_name methods, which take
    input describing the change, and query nameservers to check current prod and staging status.
    """

    @pytest.fixture(scope="module")
    def setup_checks(self):
        global config
        global chk
        global parser
        config = DnstestConfig()
        config.server_test = "test_server_stub"
        config.server_prod = "prod_server_stub"
        config.default_domain = ".example.com"
        config.have_reverse_dns = True
        dnstest.config = config

        parser = DnstestParser()
        dnstest.parser = parser

        chk = DNStestChecks(config)
        # stub
        chk.DNS.resolve_name = self.stub_resolve_name
        # stub
        chk.DNS.lookup_reverse = self.stub_lookup_reverse
        dnstest.chk = chk
        return (parser, chk)

    def stub_resolve_name(self, query, to_server, to_port=53):
        """
        stub method

        return a dict that looks like the return value from dnstest.resolve_name
        but either returns one of a hard-coded group of dicts, or an error.
        """

        if query in known_dns[to_server]:
            return {'answer': {'name': query, 'data': known_dns[to_server][query][0], 'typename': known_dns[to_server][query][1], 'classstr': 'IN', 'ttl': 360, 'type': 5, 'class': 1, 'rdlength': 14}}
        else:
            return {'status': 'NXDOMAIN'}

    def stub_lookup_reverse(self, name, to_server, to_port=53):
        """
        stub method

        return a dict that looks like the return value from dnstest.lookup_reverse
        but either returns one of a hard-coded group of dicts, or an error.
        """

        if name in known_rev_dns[to_server]:
            return {'answer': {'name': name, 'data': known_rev_dns[to_server][name], 'typename': 'PTR', 'classstr': 'IN', 'ttl': 360, 'type': 12, 'class': 1, 'rdlength': 33}}
        else:
            return {'status': 'NXDOMAIN'}

    def test_line_add(self, setup_checks):
        """
        Test end-to-end input line for adding a record
        """
        foo = dnstest.run_check_line('add record newhostname address 1.2.3.1')
        assert foo == {'message': 'newhostname => 1.2.3.1 (TEST)', 'result': True, 'secondary': ['PROD server returns NXDOMAIN for newhostname (PROD)'], 'warnings': ['REVERSE NG: got status NXDOMAIN for name 1.2.3.1 (TEST)']}

    def test_line_verify_add(self, setup_checks):
        """
        Test end-to-end input line for adding a record
        """
        foo = dnstest.run_verify_line('add record addedhostname address 1.2.3.3')
        assert foo == {'message': 'addedhostname => 1.2.3.3 (PROD)', 'result': True, 'secondary': [], 'warnings': ['REVERSE NG: got status NXDOMAIN for name 1.2.3.3 (PROD)']}
