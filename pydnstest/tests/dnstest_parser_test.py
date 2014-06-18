"""
tests for dns_parser.py

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

from pydnstest.parser import DnstestParser
from pyparsing import ParseException


class TestLanguageParsing:
    """
    Class to test the natural language parsing features of dnstest.py

    Grammars supported:
    'add (record|name|entry)? <hostname_or_fqdn> (with ?)(value|address|target)? <hostname_fqdn_or_ip>'
    'remove (record|name|entry)? <hostname_or_fqdn>'
    'rename (record|name|entry)? <hostname_or_fqdn> (with ?)(value ?) <value> to <hostname_or_fqdn>'
    'change (record|name|entry)? <hostname_or_fqdn> to <hostname_fqdn_or_ip>'
    'confirm <hostname_or_fqdn>'
    """

    @pytest.mark.parametrize(("line", "parsed_dict"), [
        ("add fooHostOne value fooHostTwo", {'operation': 'add', 'hostname': 'fooHostOne', 'value': 'fooHostTwo'}),
        ("add foobar value 10.104.92.243", {'operation': 'add', 'hostname': 'foobar', 'value': '10.104.92.243'}),
        ("add entry foobar with value baz", {'operation': 'add', 'hostname': 'foobar', 'value': 'baz'}),
        ("add record foobar.example.com target blam", {'operation': 'add', 'hostname': 'foobar.example.com', 'value': 'blam'}),
        ("add name foobar address 192.168.0.139", {'operation': 'add', 'hostname': 'foobar', 'value': '192.168.0.139'}),
        ("add foobar.example.com with target 172.16.132.10", {'operation': 'add', 'hostname': 'foobar.example.com', 'value': '172.16.132.10'}),
        ("add foobar.hosts.example.com value 172.16.132.10", {'operation': 'add', 'hostname': 'foobar.hosts.example.com', 'value': '172.16.132.10'}),
        ("remove fooHostOne", {'operation': 'remove', 'hostname': 'fooHostOne'}),
        ("remove record fooHostOne", {'operation': 'remove', 'hostname': 'fooHostOne'}),
        ("remove name fooHostOne", {'operation': 'remove', 'hostname': 'fooHostOne'}),
        ("remove entry fooHostOne", {'operation': 'remove', 'hostname': 'fooHostOne'}),
        ("remove foo.example.com", {'operation': 'remove', 'hostname': 'foo.example.com'}),
        ("remove record foo.example.com", {'operation': 'remove', 'hostname': 'foo.example.com'}),
        ("remove name foo.example.com", {'operation': 'remove', 'hostname': 'foo.example.com'}),
        ("remove entry foo.example.com", {'operation': 'remove', 'hostname': 'foo.example.com'}),
        ("remove entry foo.bar.baz.example.com", {'operation': 'remove', 'hostname': 'foo.bar.baz.example.com'}),
        ("rename fooHostOne with target targ to fooHostTwo", {'operation': 'rename', 'hostname': 'fooHostOne', 'newname': 'fooHostTwo', 'value': 'targ'}),
        ("rename entry foobar foo.bar.net to baz", {'operation': 'rename', 'hostname': 'foobar', 'newname': 'baz', 'value': 'foo.bar.net'}),
        ("rename record foobar.example.com with address 1.2.3.4 to blam", {'operation': 'rename', 'hostname': 'foobar.example.com', 'newname': 'blam', 'value': '1.2.3.4'}),
        ("rename name foobar 1.2.3.5 to baz.example.com", {'operation': 'rename', 'hostname': 'foobar', 'newname': 'baz.example.com', 'value': '1.2.3.5'}),
        ("rename foobar.example.com value 1.2.3.4 to baz.blam.hosts.example.com", {'operation': 'rename', 'hostname': 'foobar.example.com', 'newname': 'baz.blam.hosts.example.com', 'value': '1.2.3.4'}),
        ("rename foobar.hosts.example.com with value baz to blam", {'operation': 'rename', 'hostname': 'foobar.hosts.example.com', 'newname': 'blam', 'value': 'baz'}),
        ("rename foo.subdomain.example.com with value 10.188.8.76 to bar.subdomain.example.com", {'operation': 'rename', 'hostname': 'foo.subdomain.example.com', 'newname': 'bar.subdomain.example.com', 'value': '10.188.8.76'}),
        ("change fooHostOne to fooHostTwo", {'operation': 'change', 'hostname': 'fooHostOne', 'value': 'fooHostTwo'}),
        ("change foobar to 10.104.92.243", {'operation': 'change', 'hostname': 'foobar', 'value': '10.104.92.243'}),
        ("change entry foobar to baz", {'operation': 'change', 'hostname': 'foobar', 'value': 'baz'}),
        ("change record foobar.example.com to blam", {'operation': 'change', 'hostname': 'foobar.example.com', 'value': 'blam'}),
        ("change name foobar to 192.168.0.139", {'operation': 'change', 'hostname': 'foobar', 'value': '192.168.0.139'}),
        ("change foobar.example.com to 172.16.132.10", {'operation': 'change', 'hostname': 'foobar.example.com', 'value': '172.16.132.10'}),
        ("change foobar.hosts.example.com to 172.16.132.10", {'operation': 'change', 'hostname': 'foobar.hosts.example.com', 'value': '172.16.132.10'}),
        ("change entry foobar.hosts.example.com to 172.16.132.10", {'operation': 'change', 'hostname': 'foobar.hosts.example.com', 'value': '172.16.132.10'}),
        ("change name foobar to foobar.hosts.example.com", {'operation': 'change', 'hostname': 'foobar', 'value': 'foobar.hosts.example.com'}),
        ("change name foobar to foobar.example.com", {'operation': 'change', 'hostname': 'foobar', 'value': 'foobar.example.com'}),
        ("confirm foo.example.com", {'operation': 'confirm', 'hostname': 'foo.example.com'}),
        ("confirm record foo.example.com", {'operation': 'confirm', 'hostname': 'foo.example.com'}),
        ("confirm entry foo.example.com", {'operation': 'confirm', 'hostname': 'foo.example.com'}),
        ("confirm name foo.example.com", {'operation': 'confirm', 'hostname': 'foo.example.com'}),
        ("confirm 1.2.3.4", None),
        ("confirm record 1.2.3.4", None),
        ("confirm entry 1.2.3.4", None),
        ("confirm name 1.2.3.4", None),
        ("confirm foo", {'operation': 'confirm', 'hostname': 'foo'}),
        ("confirm record foo", {'operation': 'confirm', 'hostname': 'foo'}),
        ("confirm entry foo", {'operation': 'confirm', 'hostname': 'foo'}),
        ("confirm name foo", {'operation': 'confirm', 'hostname': 'foo'}),
        ("confirm m.example.com", {'operation': 'confirm', 'hostname': 'm.example.com'}),
        ("confirm foo.m.example.com", {'operation': 'confirm', 'hostname': 'foo.m.example.com'}),
        ("confirm m", {'operation': 'confirm', 'hostname': 'm'}),
        ("confirm m._foo.example.com", {'operation': 'confirm', 'hostname': 'm._foo.example.com'}),
        ("confirm _bar.example.com", {'operation': 'confirm', 'hostname': '_bar.example.com'}),
        ("add record _foobar.example.com address 1.2.3.4", {'operation': 'add', 'hostname': '_foobar.example.com', 'value': '1.2.3.4'}),
        ("add record foobar._discover.example.com target blam", {'operation': 'add', 'hostname': 'foobar._discover.example.com', 'value': 'blam'})
    ])
    def test_parse_should_succeed(self, line, parsed_dict):
        foo = None
        try:
            p = DnstestParser()
            foo = p.parse_line(line)
        except ParseException:
            # assert will fail, no need to do anything here
            pass
        assert foo == parsed_dict

    @pytest.mark.parametrize("line", [
        "add extraword record foobar.example.com target blam",
        "add foobar value blam extraword",
        "remove foo blam",
        "rename foobar.example.com to baz.blam.hosts.example.com EXTRAWORD"
        "change foobar",
        "change foobar to",
        "change foobar.hosts.example.com to",
        "add m.foo.example.com with target foo.example.com.edgesuite.net.",
    ])
    def test_parse_should_raise_exception(self, line):
        with pytest.raises(ParseException):
            p = DnstestParser()
            p.parse_line(line)

    def test_get_grammar(self):
        p = DnstestParser()
        expected = ['add (record|name|entry)? <hostname_or_fqdn> (with ?)(value|address|target)? <hostname_fqdn_or_ip>',
                    'remove (record|name|entry)? <hostname_or_fqdn>',
                    'rename (record|name|entry)? <hostname_or_fqdn> (with ?)(value ?) <value> to <hostname_or_fqdn>',
                    'change (record|name|entry)? <hostname_or_fqdn> to <hostname_fqdn_or_ip>',
                    'confirm (record|name|entry)? <hostname_or_fqdn>',
                    ]
        result = p.get_grammar()
        assert result == expected
