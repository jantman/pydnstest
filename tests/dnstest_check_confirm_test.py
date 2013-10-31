# tests for dns_parser.py

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../')

from dnstest_checks import DNStestChecks
from dnstest_config import DnstestConfig

"""
This dict stores the DNS results that our DNS-mocking functions will return.
Format of the 'known_dns' dict:
[prod|test] - whether this is for the prod or test DNS server
    [fwd|rev] - whether this is forward or reverse DNS
        [recordname] - the name of this record, as sent to the DNS query methods
            = value - a string or list of the record value, see below
value can be:
for 'rev' dns:
  <currently not implemented>
for 'fwd' dns:
  - a dict with key "status" and value of the 'status' attribute of the DNS result
  - a dict with keys and values that match the answer section of the DNS query, i.e.:
    {'name': 'foo.example.com', 'data': '10.188.14.211', 'typename': 'A', 'classstr': 'IN', 'ttl': 360, 'type': 1, 'class': 1, 'rdlength': 4}
"""
known_dns = {'test': {'fwd': {}, 'rev': {}}, 'prod': {'fwd': {}, 'rev': {}}}

"""
This is a dict of dicts, each one corresponding to a single test case, and
having the following elements:
'oldname' - the old DNS record to be renamed
'newname' - what to rename that to
'value' - the value of the DNS record to rename
'result_chk' - the expected return dict for the check operation
'result_ver' - the expected return dict for the verify operation
"""
TESTS = {}

"""
Here we define all of the tests, along with their expected results for
check and verify, and the DNS entries that each test uses.
"""

# test 0 - test returns NXDOMAIN, prod returns answer
known_dns['prod']['fwd']['hostname_test0.example.com'] = {'name': 'hostname_test0.example.com', 'data': '1.2.8.1', 'typename': 'A', 'classstr': 'IN', 'ttl': 360, 'type': 1, 'class': 1, 'rdlength': 4}
TESTS[0] = {'hostname': 'hostname_test0', 'result': {'message': 'test server returned status NXDOMAIN for name hostname_test0, but prod returned valid answer of 1.2.8.1', 'result': False, 'secondary': [], 'warnings': []}}

# test 1 - test and prod both return NXDOMAIN
TESTS[1] = {'hostname': 'hostname_test1', 'result': {'message': 'both test and prod returned status NXDOMAIN for name hostname_test1', 'result': True, 'secondary': [], 'warnings': []}}

# test 2 - test returns answer, prod returns NXDOMAIN
known_dns['test']['fwd']['hostname_test2.example.com'] = {'name': 'hostname_test2.example.com', 'data': '1.2.8.1', 'typename': 'A', 'classstr': 'IN', 'ttl': 360, 'type': 1, 'class': 1, 'rdlength': 4}
TESTS[2] = {'hostname': 'hostname_test2', 'result': {'message': 'prod server returned status NXDOMAIN for name hostname_test2, but test returned valid answer of 1.2.8.1', 'result': False, 'secondary': [], 'warnings': []}}

# test 3 - both return answer, test includes key not in prod
known_dns['test']['fwd']['hostname_test3.example.com'] = {'name': 'hostname_test3.example.com', 'data': '1.2.8.1', 'typename': 'A', 'classstr': 'IN', 'ttl': 360, 'type': 1, 'class': 1, 'rdlength': 4}
known_dns['prod']['fwd']['hostname_test3.example.com'] = {'name': 'hostname_test3.example.com', 'data': '1.2.8.1', 'typename': 'A', 'classstr': 'IN', 'type': 1, 'class': 1, 'rdlength': 4}
TESTS[3] = {'hostname': 'hostname_test3', 'result': {'message': "prod and test servers return different responses for 'hostname_test3'", 'result': False, 'secondary': [], 'warnings': ["NG: test response has ttl of '360'; prod response does not include ttl"]}}

# test 4 - both return answer, test and prod have a differing value for a key
known_dns['test']['fwd']['hostname_test4.example.com'] = {'name': 'hostname_test4.example.com', 'data': '1.2.8.1', 'typename': 'A', 'classstr': 'IN', 'ttl': 360, 'type': 1, 'class': 1, 'rdlength': 4}
known_dns['prod']['fwd']['hostname_test4.example.com'] = {'name': 'hostname_test4.example.com', 'data': '1.2.8.1', 'typename': 'A', 'classstr': 'IN', 'ttl': 900, 'type': 1, 'class': 1, 'rdlength': 4}
TESTS[4] = {'hostname': 'hostname_test4', 'result': {'message': "prod and test servers return different responses for 'hostname_test4'", 'result': False, 'secondary': [], 'warnings': ["NG: test response has ttl of '360' but prod response has '900'"]}}

# test 5 - both return answer, test and prod have differing values for 2 keys
known_dns['test']['fwd']['hostname_test5.example.com'] = {'name': 'hostname_test5.example.com', 'data': '1.2.8.1', 'typename': 'A', 'classstr': 'IN', 'ttl': 360, 'type': 1, 'class': 1, 'rdlength': 4}
known_dns['prod']['fwd']['hostname_test5.example.com'] = {'name': 'hostname_test5.example.com', 'data': '1.2.8.2', 'typename': 'A', 'classstr': 'IN', 'ttl': 900, 'type': 1, 'class': 1, 'rdlength': 4}
TESTS[5] = {'hostname': 'hostname_test5', 'result': {'message': "prod and test servers return different responses for 'hostname_test5'", 'result': False, 'secondary': [], 'warnings': ["NG: test response has ttl of '360' but prod response has '900'", "NG: test response has data of '1.2.8.1' but prod response has '1.2.8.2'"]}}

# test 6 - both return answer, prod includes key not in test
known_dns['test']['fwd']['hostname_test6.example.com'] = {'name': 'hostname_test6.example.com', 'data': '1.2.8.1', 'typename': 'A', 'classstr': 'IN', 'type': 1, 'class': 1, 'rdlength': 4}
known_dns['prod']['fwd']['hostname_test6.example.com'] = {'name': 'hostname_test6.example.com', 'data': '1.2.8.1', 'typename': 'A', 'classstr': 'IN', 'ttl': 360, 'type': 1, 'class': 1, 'rdlength': 4}
TESTS[6] = {'hostname': "hostname_test6", 'result': {'message': "prod and test servers return different responses for 'hostname_test6'", 'result': False, 'secondary': [], 'warnings': ["NG: prod response has ttl of '360'; test response does not include ttl"]}}

# test 7 - OK, same
known_dns['test']['fwd']['hostname_test7.example.com'] = {'name': 'hostname_test7.example.com', 'data': '1.2.8.1', 'typename': 'A', 'classstr': 'IN', 'ttl': 360, 'type': 1, 'class': 1, 'rdlength': 4}
known_dns['prod']['fwd']['hostname_test7.example.com'] = {'name': 'hostname_test7.example.com', 'data': '1.2.8.1', 'typename': 'A', 'classstr': 'IN', 'ttl': 360, 'type': 1, 'class': 1, 'rdlength': 4}
TESTS[7] = {'hostname': "hostname_test7", 'result': {'message': "prod and test servers return same response for 'hostname_test7'", 'result': True, 'secondary': ["response: {'typename': 'A', 'name': 'hostname_test7.example.com', 'ttl': 360, 'type': 1, 'data': '1.2.8.1', 'class': 1, 'rdlength': 4, 'classstr': 'IN'}"], 'warnings': []}}

# test 8 - both return NXDOMAIN
TESTS[8] = {'hostname': 'hostname_test8', 'result': {'message': 'both test and prod returned status NXDOMAIN for name hostname_test8', 'result': True, 'secondary': [], 'warnings': []}}

# test 9 - both return SERVFAIL
known_dns['test']['fwd']['hostname_test9.example.com'] = {'status': 'SERVFAIL'}
known_dns['prod']['fwd']['hostname_test9.example.com'] = {'status': 'SERVFAIL'}
TESTS[9] = {'hostname': 'hostname_test9', 'result': {'message': 'both test and prod returned status SERVFAIL for name hostname_test9', 'result': True, 'secondary': [], 'warnings': []}}

# test 10 - prod SERVFAIL and test NXDOMAIN
known_dns['prod']['fwd']['hostname_test10.example.com'] = {'status': 'SERVFAIL'}
TESTS[10] = {'hostname': 'hostname_test10', 'result': {'message': 'test server returned status NXDOMAIN for name hostname_test10, but prod returned status SERVFAIL', 'result': False, 'secondary': [], 'warnings': []}}


class TestDNSCheckConfirm:
    """
    Test DNS checks, using stubbed name resolution methods that return static values.

    The code in this class checks the logic of dnstest.py's confirm_name method, which takes
    a record name and verifies that the results are the same from prod and test servers.
    """

    @pytest.fixture(scope="module")
    def setup(self):
        """
        Sets up test environment for tests of check methods,
        including redefining resolve_name and lookup_reverse
        to the appropriate methods in this class
        """
        config = DnstestConfig()
        config.server_test = "test"
        config.server_prod = "prod"
        config.default_domain = ".example.com"
        config.have_reverse_dns = True

        chk = DNStestChecks(config)
        # stub
        chk.DNS.resolve_name = self.stub_resolve_name
        # stub
        chk.DNS.lookup_reverse = self.stub_lookup_reverse
        return chk

    def stub_resolve_name(self, query, to_server, to_port=53):
        """
        DNS stub method

        return a dict that looks like the return value from dnstest.resolve_name
        but either returns one of a hard-coded group of dicts, or an error.
        """

        if query in known_dns[to_server]['fwd'] and 'status' in known_dns[to_server]['fwd'][query]:
            return {'status': known_dns[to_server]['fwd'][query]['status']}
        elif query in known_dns[to_server]['fwd']:
            return {'answer': known_dns[to_server]['fwd'][query]}
        else:
            return {'status': 'NXDOMAIN'}

    def stub_lookup_reverse(self, name, to_server, to_port=53):
        """
        DNS stub method

        return a dict that looks like the return value from dnstest.lookup_reverse
        but either returns one of a hard-coded group of dicts, or an error.
        """

        if name in known_dns[to_server]['rev'] and known_dns[to_server]['rev'][name] == "SERVFAIL":
            return {'status': 'SERVFAIL'}
        elif name in known_dns[to_server]['rev']:
            return {'answer': {'name': name, 'data': known_dns[to_server]['rev'][name], 'typename': 'PTR', 'classstr': 'IN', 'ttl': 360, 'type': 12, 'class': 1, 'rdlength': 33}}
        else:
            return {'status': 'NXDOMAIN'}

    ###########################################
    # Done with setup, start the actual tests #
    ###########################################

    def test_confirm(self):
        """
        Run all of the tests from the TESTS dict, via yield
        """
        s = self.setup()
        for t in TESTS:
            tst = TESTS[t]
            yield "test_confirm chk TESTS[%d]" % t, self.dns_confirm, s, tst['hostname'], tst['result']

    def dns_confirm(self, setup, hostname, result):
        """
        Test checks for verifying an added record
        """
        foo = setup.confirm_name(hostname)
        assert foo == result
