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
[chk|ver] - whether this is pre-change (_check methods) or post-change (_verify methods)
    [prod|test] - whether this is for the prod or test DNS server
        [fwd|rev] - whether this is forward or reverse DNS
            [recordname] - the name of this record, as sent to the DNS query methods
                = value - a string or list of the record value, see below
value can be:
for 'rev' dns:
  - a string with the value of the PTR record
  - the string "SERVFAIL", which returns a SERVFAIL result
for 'fwd' dns:
  - a list whose first item is "STATUS", and whose second item is the 'status' attribute of the DNS result
  - a list whose first item is the data/value of the record, and whose second item is the typename of the record (i.e. "A" or "CNAME")
"""
known_dns = {'chk': {'test': {'fwd': {}, 'rev': {}}, 'prod': {'fwd': {}, 'rev': {}}}, 'ver': {'test': {'fwd': {}, 'rev': {}}, 'prod': {'fwd': {}, 'rev': {}}}}

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

# test 0
TESTS[0] = {'hostname': "badhostname"}
TESTS[0]['result_chk'] = {'message': "badhostname got status NXDOMAIN from PROD - cannot remove a name that doesn't exist (PROD)", 'secondary': [], 'result': False, 'warnings': []}

# test 1
TESTS[1] = {'hostname': "prodonlyhostname"}
known_dns['chk']['prod']['fwd']['prodonlyhostname.example.com'] = ['1.2.3.5', 'A']
TESTS[1]['result_chk'] = {'message': 'prodonlyhostname removed, got status NXDOMAIN (TEST)', 'result': True, 'secondary': ['PROD value was 1.2.3.5 (PROD)'], 'warnings': []}

# test 2
TESTS[2] = {'hostname': "addedhostname"}
known_dns['chk']['prod']['fwd']['addedhostname.example.com'] = ['1.2.3.3', 'A']
known_dns['chk']['test']['fwd']['addedhostname.example.com'] = ['1.2.3.3', 'A']
TESTS[2]['result_chk'] = {'message': 'addedhostname returned valid answer, not removed (TEST)', 'result': False, 'secondary': [], 'warnings': []}

# test 3
TESTS[3] = {'hostname': "prodonlywithrev"}
known_dns['chk']['prod']['fwd']['prodonlywithrev.example.com'] = ['1.2.3.6', 'A']
known_dns['chk']['prod']['rev']['1.2.3.6'] = 'prodonlywithrev.example.com'
TESTS[3]['result_chk'] = {'message': 'prodonlywithrev removed, got status NXDOMAIN (TEST)', 'result': True, 'secondary': ['PROD value was 1.2.3.6 (PROD)'], 'warnings': []}

# test 4
TESTS[4] = {'hostname': "prodwithtestrev"}
known_dns['chk']['prod']['rev']['1.2.3.7'] = 'prodwithtestrev.example.com'
known_dns['chk']['test']['rev']['1.2.3.7'] = 'prodwithtestrev.example.com'
known_dns['chk']['prod']['fwd']['prodwithtestrev.example.com'] = ['1.2.3.7', 'A']
TESTS[4]['result_chk'] = {'message': 'prodwithtestrev removed, got status NXDOMAIN (TEST)', 'result': True, 'secondary': ['PROD value was 1.2.3.7 (PROD)'], 'warnings': ['prodwithtestrev appears to still have reverse DNS set to prodwithtestrev.example.com (TEST)']}

# test 5
TESTS[5] = {'hostname': "servfail-test"}
known_dns['chk']['test']['fwd']['servfail-test.example.com'] = ['STATUS', 'SERVFAIL']
known_dns['chk']['prod']['fwd']['servfail-test.example.com'] = ['1.2.3.8', 'A']
TESTS[5]['result_chk'] = {'message': 'servfail-test returned status SERVFAIL (TEST)', 'result': False, 'secondary': [], 'warnings': []}

# test 6
TESTS[6] = {'hostname': "notahostname"}
TESTS[6]['result_ver'] = {'message': 'notahostname removed, got status NXDOMAIN (PROD)', 'result': True, 'secondary': [], 'warnings': []}

# test 7
TESTS[7] = {'hostname': "existinghostname"}
known_dns['ver']['prod']['fwd']['existinghostname.example.com'] = ['1.2.3.2', 'A']
TESTS[7]['result_ver'] = {'message': "existinghostname returned valid answer of '1.2.3.2', not removed (PROD)", 'result': False, 'secondary': [], 'warnings': []}

# test 8
TESTS[8] = {'hostname': "newhostname"}
known_dns['ver']['test']['fwd']['newhostname.example.com'] = ['1.2.3.1', 'A']
TESTS[8]['result_ver'] = {'message': 'newhostname removed, got status NXDOMAIN (PROD)', 'result': True, 'secondary': ['newhostname returned answer 1.2.3.1 (TEST)'], 'warnings': []}

# test 9
TESTS[9] = {'hostname': "servfail-prod"}
known_dns['ver']['prod']['fwd']['servfail-prod.example.com'] = ['STATUS', 'SERVFAIL']
TESTS[9]['result_ver'] = {'message': "servfail-prod returned a 'strange' status of SERVFAIL (PROD)", 'result': False, 'secondary': [], 'warnings': []}

# test 10
TESTS[10] = {'hostname': "removetest1"}
known_dns['ver']['test']['fwd']['removetest1.example.com'] = ['1.2.3.27', 'A']
TESTS[10]['result_ver'] = {'message': 'removetest1 removed, got status NXDOMAIN (PROD)', 'result': True, 'secondary': ['removetest1 returned answer 1.2.3.27 (TEST)'], 'warnings': []}


class TestDNSCheckRemove:
    """
    Test DNS checks, using stubbed name resolution methods that return static values.

    The code in this class checks the logic of dnstest.py's test_*_name methods, which take
    input describing the change, and query nameservers to check current prod and staging status.
    """

    @pytest.fixture(scope="module")
    def setup_checks(self):
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

    @pytest.fixture(scope="module")
    def setup_verifies(self):
        """
        Sets up test environment for tests of verify methods,
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
        chk.DNS.resolve_name = self.stub_resolve_name_verify
        # stub
        chk.DNS.lookup_reverse = self.stub_lookup_reverse_verify
        return chk

    def stub_resolve_name(self, query, to_server, to_port=53):
        """
        DNS stub method

        return a dict that looks like the return value from dnstest.resolve_name
        but either returns one of a hard-coded group of dicts, or an error.
        """

        if query in known_dns['chk'][to_server]['fwd'] and known_dns['chk'][to_server]['fwd'][query][0] == "STATUS":
            return {'status': known_dns['chk'][to_server]['fwd'][query][1]}
        elif query in known_dns['chk'][to_server]['fwd']:
            return {'answer': {'name': query, 'data': known_dns['chk'][to_server]['fwd'][query][0], 'typename': known_dns['chk'][to_server]['fwd'][query][1], 'classstr': 'IN', 'ttl': 360, 'type': 5, 'class': 1, 'rdlength': 14}}
        else:
            return {'status': 'NXDOMAIN'}

    def stub_lookup_reverse(self, name, to_server, to_port=53):
        """
        DNS stub method

        return a dict that looks like the return value from dnstest.lookup_reverse
        but either returns one of a hard-coded group of dicts, or an error.
        """

        if name in known_dns['chk'][to_server]['rev'] and known_dns['chk'][to_server]['rev'][name] == "SERVFAIL":
            return {'status': 'SERVFAIL'}
        elif name in known_dns['chk'][to_server]['rev']:
            return {'answer': {'name': name, 'data': known_dns['chk'][to_server]['rev'][name], 'typename': 'PTR', 'classstr': 'IN', 'ttl': 360, 'type': 12, 'class': 1, 'rdlength': 33}}
        else:
            return {'status': 'NXDOMAIN'}

    def stub_resolve_name_verify(self, query, to_server, to_port=53):
        """
        DNS stub method

        return a dict that looks like the return value from dnstest.resolve_name
        but either returns one of a hard-coded group of dicts, or an error.
        """

        if query in known_dns['ver'][to_server]['fwd'] and known_dns['ver'][to_server]['fwd'][query][0] == "STATUS":
            return {'status': known_dns['ver'][to_server]['fwd'][query][1]}
        elif query in known_dns['ver'][to_server]['fwd']:
            return {'answer': {'name': query, 'data': known_dns['ver'][to_server]['fwd'][query][0], 'typename': known_dns['ver'][to_server]['fwd'][query][1], 'classstr': 'IN', 'ttl': 360, 'type': 5, 'class': 1, 'rdlength': 14}}
        else:
            return {'status': 'NXDOMAIN'}

    def stub_lookup_reverse_verify(self, name, to_server, to_port=53):
        """
        DNS stub method

        return a dict that looks like the return value from dnstest.lookup_reverse
        but either returns one of a hard-coded group of dicts, or an error.
        """

        if name in known_dns['ver'][to_server]['rev'] and known_dns['ver'][to_server]['rev'][name] == "SERVFAIL":
            return {'status': 'SERVFAIL'}
        elif name in known_dns['ver'][to_server]['rev']:
            return {'answer': {'name': name, 'data': known_dns['ver'][to_server]['rev'][name], 'typename': 'PTR', 'classstr': 'IN', 'ttl': 360, 'type': 12, 'class': 1, 'rdlength': 33}}
        else:
            return {'status': 'NXDOMAIN'}

    ###########################################
    # Done with setup, start the actual tests #
    ###########################################

    def test_remove(self):
        """
        Run all of the tests from the TESTS dict, via yield
        """
        sc = self.setup_checks()
        sv = self.setup_verifies()
        for t in TESTS:
            tst = TESTS[t]
            if 'result_chk' in tst:
                yield self.dns_remove, sc, tst['hostname'], tst['result_chk']
            if 'result_ver' in tst:
                yield self.dns_verify_remove, sv, tst['hostname'], tst['result_ver']

    def dns_remove(self, setup_checks, hostname, result):
        """
        Test checks for removing a record from DNS
        """
        foo = setup_checks.check_removed_name(hostname)
        assert foo == result

    def dns_verify_remove(self, setup_checks, hostname, result):
        """
        Test checks for verifying a removed record
        """
        foo = setup_checks.verify_removed_name(hostname)
        assert foo == result