# tests for dnstest_dns.py
#
# This class is just a light wrapper around the DNS module.
# These tests really only exist to make sure that DNS doesn't
# change or break its API without us noticing.
#
# BE WARNED that the DNS lookups used here *may* fail if the author's
# hosting setup changes drastically.
#

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../')

from dnstest_dns import DNStestDNS


class TestDNS:
    """
    tests for dnstest_dns.py / DNStestDNS

    The class being tested is just a light wrapper around the DNS module.
    These tests really only exist to make sure that DNS doesn't
    change or break its API without us noticing.

    BE WARNED that the DNS lookups used here *may* fail if the author's
    hosting setup changes drastically.
    """

    @pytest.fixture(scope="module")
    def test_DNS(self):
        DNS = DNStestDNS()
        return DNS

    def test_resolve_name_A(self, test_DNS):
        """
        Test that a should-be-correct A record is resolved correctly.
        """

        query = "linode2.jasonantman.com"
        server = "ns1.linode.com"
        result = {'answer': {'class': 1, 'classstr': 'IN', 'data': '96.126.107.19', 'name': 'linode2.jasonantman.com', 'rdlength': 4, 'ttl': 86400, 'type': 1, 'typename': 'A'}}

        foo = test_DNS.resolve_name(query, server)
        assert foo == result

    def test_resolve_name_CNAME(self, test_DNS):
        """
        Test that a should-be-correct CNAME is resolved correctly (server can't return an A answer).
        """

        query = "pydnstest1.jasonantman.com"
        server = "ns1.linode.com"
        result = {'answer': {'class': 1, 'classstr': 'IN', 'data': 'github.com', 'name': 'pydnstest1.jasonantman.com', 'rdlength': 9, 'ttl': 86400, 'type': 5, 'typename': 'CNAME'}}

        foo = test_DNS.resolve_name(query, server)
        assert foo == result

    def test_resolve_name_nxdomain(self, test_DNS):
        """
        Test that a should-be-nxdomain name is returned as such.
        """

        query = "notaname.jasonantman.com"
        server = "ns1.linode.com"
        result = {'status': 'NXDOMAIN'}

        foo = test_DNS.resolve_name(query, server)
        assert foo == result

    def test_lookup_reverse(self, test_DNS):
        """
        Test that a given reverse DNS lookup is correct.
        """

        query = "96.126.107.19"
        server = "ns1.linode.com"
        result = {'answer': {'class': 1, 'classstr': 'IN', 'data': 'linode2.jasonantman.com', 'name': '19.107.126.96.in-addr.arpa', 'rdlength': 25, 'ttl': 86400, 'type': 12, 'typename': 'PTR'}}

        foo = test_DNS.lookup_reverse(query, server)
        assert foo == result

    def test_lookup_reverse_nxdomain(self, test_DNS):
        """
        Test that a should-be-nxdomain reverse lookup is returned as such.

        Linode should REFUSE a query for a domain it's not authoritative for.
        """

        query = "66.6.152.59"
        server = "ns1.linode.com"
        result = {'status': 'REFUSED'}

        foo = test_DNS.lookup_reverse(query, server)
        assert foo == result
