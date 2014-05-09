"""
sanity checks for the upstream DNS package

This class is just a light wrapper around the DNS module.
These tests really only exist to make sure that DNS doesn't
change or break its API without us noticing.

BE WARNED that the DNS lookups used here *may* fail if the author's
hosting setup changes drastically.

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

from pydnstest.dns import DNStestDNS
import DNS


class AnswerObject(object):
    pass


class EmptyAnswer(object):

    def req(self):
        A = AnswerObject()
        b = ['one', 'two']
        setattr(A, 'answers', b)
        return A


class MultipleAnswer(object):

    def req(self):
        A = AnswerObject()
        b = []
        setattr(A, 'answers', b)
        return A


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
        result = {'answer': {'class': 1, 'classstr': 'IN', 'data': '96.126.107.19', 'name': 'linode2.jasonantman.com', 'rdlength': 4, 'ttl': 3600, 'type': 1, 'typename': 'A'}}

        foo = test_DNS.resolve_name(query, server)
        assert foo == result

    def test_resolve_name_CNAME(self, test_DNS):
        """
        Test that a should-be-correct CNAME is resolved correctly (server can't return an A answer).
        """

        query = "pydnstest1.jasonantman.com"
        server = "ns1.linode.com"
        result = {'answer': {'class': 1, 'classstr': 'IN', 'data': 'github.com', 'name': 'pydnstest1.jasonantman.com', 'rdlength': 9, 'ttl': 3600, 'type': 5, 'typename': 'CNAME'}}

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

    def test_multiple_answer(self, test_DNS, monkeypatch):
        """
        Test for something that returns multiple answers.
        """

        query = "foo.example.com"
        server = "ns.example.com"
        result = {'answer': 'one'}

        def mockreturn(name=None, server=None, qtype=None, port=None):
            if qtype == "CNAME":
                a = EmptyAnswer()
                return a
            a = MultipleAnswer()
            return a

        monkeypatch.setattr(DNS, "Request", mockreturn)

        foo = test_DNS.resolve_name(query, server)
        assert foo == result
