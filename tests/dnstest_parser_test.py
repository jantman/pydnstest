# tests for dns_parser.py

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../')

from dnstest_parser import DnstestParser
from pyparsing import ParseException


class TestLanguageParsing:
    """
    Class to test the natural language parsing features of dnstest.py

    Grammars supported:
    'add (record|name|entry)? <hostname_or_fqdn> (with ?)(value|address|target)? <hostname_fqdn_or_ip>'
    'remove (record|name|entry)? <hostname_or_fqdn>'
    'rename (record|name|entry)? <hostname_or_fqdn> (with ?)(value ?) <value> to <hostname_or_fqdn>'
    'change (record|name|entry)? <hostname_or_fqdn> to <hostname_fqdn_or_ip>'
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
    ])
    def test_parse_should_succeed(self, line, parsed_dict):
        foo = None
        try:
            p = DnstestParser()
            foo = p.parse_line(line).asDict()
        except ParseException, err:
            print err.line
            print " " * (err.column - 1) + "^"
            print err
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
