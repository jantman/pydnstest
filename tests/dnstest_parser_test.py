# tests for dns_parser.py

import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../')

import dnstest_parser
from pyparsing import ParseException

class TestLanguageParsing:
    """
    Class to test the natural language parsing features of dnstest.py

    Grammars supported:
    'add (record|name|entry)? <hostname_or_fqdn> (with ?)(value|address|target)? <hostname_fqdn_or_ip>'
    'remove (record|name|entry)? <hostname_or_fqdn>'
    'rename (record|name|entry)? <hostname_or_fqdn> to <hostname_or_fqdn>'
    'change (record|name|entry)? <hostname_or_fqdn> to <hostname_fqdn_or_ip>'
    '(set )?reverse( for)? (record|name|entry)? <hostname_or_fqdn> to <hostname_or_fqdn>'
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

    ])
    def test_parse_should_succeed(self, line, parsed_dict):
        assert dnstest_parser.parse_line(line).asDict() == parsed_dict
    
    @pytest.mark.parametrize("line", [
        "add extraword record foobar.example.com target blam",
        "add foobar value blam extraword",
        "remove foo blam",
        "remove record 10.23.45.67",
        "remove 10.23.45.67",
    ])
    def test_parse_should_raise_exception(self, line):
        with pytest.raises(ParseException):
            dnstest_parser.parse_line(line)
