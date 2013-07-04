# tests for dns_parser.py

import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../')

import dnstest_parser
from pyparsing import ParseException

class TestParseAdd:

    @pytest.mark.parametrize("param", [
        ("add fooHostOne value fooHostTwo", {'operation': 'add', 'hostname': 'fooHostOne', 'value': 'fooHostTwo'}),
        ("add foobar value 10.104.92.243", {'operation': 'add', 'hostname': 'foobar', 'value': '10.104.92.243'}),
        ("add host foobar with value baz", {'operation': 'add', 'hostname': 'foobar', 'value': 'baz'}),
        ("add record foobar.example.com target blam", {'operation': 'add', 'hostname': 'foobar.example.com', 'value': 'blam'}),
    ])
    def test_parse_add_success(self, param):
        assert dnstest_parser.parse_line(param[0]).asDict() == param[1]
    
    
    @pytest.mark.parametrize("param", [
        "add extraword record foobar.example.com target blam",
        "add foobar value blam extraword",
    ])
    def test_parse_add_should_fail(self, param):
        with pytest.raises(ParseException):
            dnstest_parser.parse_line(param).asDict()
