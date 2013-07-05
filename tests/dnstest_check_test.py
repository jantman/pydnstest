# tests for dns_parser.py

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../')

import dnstest_checks


# dict of known (mocked) reverse DNS values for test and prod servers
known_rev_dns = {'test_server_stub': {}, 'prod_server_stub': {}}
known_rev_dns['test_server_stub']['10.188.12.10'] = 'foo.example.com'

# dict of known (mocked) forward DNS values for test and prod servers
# each known_dns[server][name] is [value, record_type]
known_dns = {'test_server_stub': {}, 'prod_server_stub': {}}
known_dns['test_server_stub']['newhostname.example.com'] = ['1.2.3.1', 'A']
known_dns['prod_server_stub']['existinghostname.example.com'] = ['1.2.3.2', 'A']


class TestDNSChecks:
    """
    Test DNS checks, using stubbed name resolution methods that return static values.

    The code in this class checks the logic of dnstest.py's test_*_name methods, which take
    input describing the change, and query nameservers to check current prod and staging status.
    """

    config = {'defaults': {'domain': '.example.com', 'have_reverse_dns': True}, 'servers': {'test': 'test_server_stub', 'prod': 'prod_server_stub'}}

    def stub_resolve_name(query, to_server, to_port=53):
        """
        stub method

        return a dict that looks like the return value from dnstest.resolve_name
        but either returns one of a hard-coded group of dicts, or an error.
        """

        if query in known_dns[to_server]:
            return {'answer': {'name': query, 'data': known_dns[to_server][query][0], 'typename': known_dns[to_server][query][1], 'classstr': 'IN', 'ttl': 360, 'type': 5, 'class': 1, 'rdlength': 14}}
        else:
            return {'status': 'NXDOMAIN'}

    # stub
    dnstest_checks.resolve_name = stub_resolve_name

    def stub_lookup_reverse(name, to_server, to_port=53):
        """
        stub method

        return a dict that looks like the return value from dnstest.lookup_reverse
        but either returns one of a hard-coded group of dicts, or an error.
        """

        if name in self.known_rev_dns[to_server]:
            #a = name.split('.')
            #a.reverse()
            #rev_name = '.'.join(a) + '.in-addr.arpa'
            return {'answer': {'name': name, 'data': known_rev_dns[to_server][name], 'typename': 'PTR', 'classstr': 'IN', 'ttl': 360, 'type': 12, 'class': 1, 'rdlength': 33}}
        else:
            return {'status': 'NXDOMAIN'}

    # stub
    dnstest_checks.lookup_reverse = stub_lookup_reverse

    def test_dns_add(self):
        """
        Test checks for adding a record to DNS
        """
        added = {'newhostname': '1.2.3.1'}
        foo = dnstest_checks.check_added_names(added)
        assert foo == None

    def test_dns_add_already_in_prod(self):
        """
        Test for adding a record that's already in prod
        """
        global config
        config = self.config
        added = {'existinghostname': '1.2.3.2'}
        foo = dnstest_checks.check_added_names(added)
        assert foo == False
