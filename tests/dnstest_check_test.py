# tests for dns_parser.py

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../')

import dnstest


class TestDNSChecks:
    """
    Test DNS checks, using stubbed name resolution methods that return static values.

    The code in this class checks the logic of dnstest.py's test_*_name methods, which take
    input describing the change, and query nameservers to check current prod and staging status.
    """

    def stub_resolve_name(query, to_server, default_domain, to_port=53):
        """
        stub method

        return a dict that looks like the return value from dnstest.resolve_name
        but either returns one of a hard-coded group of dicts, or an error.
        """

        #return {'answer': a.answers[0]}
        return {'status': a.header['status']}

    # stub
    dnstest.resolve_name = stub_resolve_name

    def stub_lookup_reverse(name, to_server, to_port=53):
        """
        stub method

        return a dict that looks like the return value from dnstest.lookup_reverse
        but either returns one of a hard-coded group of dicts, or an error.
        """
        #return {'answer': a.answers[0]}
        return {'status': a.header['status']}

    # stub
    dnstest.lookup_reverse = stub_lookup_reverse

    def test_dns_add(self):
        """
        Test checks for adding a record to DNS
        """
        added = {'newhostname': '1.2.3.4'}
        foo = check_added_names(added, 'test_server_stub', 'prod_server_stub', '.example.com', False)
        assert foo == None
