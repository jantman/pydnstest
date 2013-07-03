# tests for dns_parser.py

import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../')

import dnstest_parser

class TestParseAdd:

    @pytest.mark.parameterize("input,expected", [
        ("add fooHostOne value fooHostTwo", {'operation': 'add', 'hostname': 'fooHostOne', 'value': 'fooHostTwo'}),
    ])
    def test_parse_add(self, input, expected):
        res = dnstest_parser.parse_line(input)
        res_dict = res.asDict()
        assert res_dict == expected

