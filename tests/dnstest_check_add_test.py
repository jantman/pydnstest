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
TESTS[0] = {'hostname': "newhostname", 'value': "1.2.3.1"}
known_dns['chk']['test']['fwd']['newhostname.example.com'] = ['1.2.3.1', 'A']
TESTS[0]['result_chk'] = {'message': 'newhostname => 1.2.3.1 (TEST)', 'result': True, 'secondary': ['PROD server returns NXDOMAIN for newhostname (PROD)'], 'warnings': ['REVERSE NG: got status NXDOMAIN for name 1.2.3.1 (TEST)']}

# test 1
TESTS[1] = {'hostname': "existinghostname", 'value': "1.2.3.2"}
known_dns['chk']['prod']['fwd']['existinghostname.example.com'] = ['1.2.3.2', 'A']
TESTS[1]['result_chk'] = {'message': 'new name existinghostname returned valid result from prod server (PROD)', 'result': False, 'secondary': [], 'warnings': []}

# test 2
TESTS[2] = {'hostname': "host-no-reverse", 'value': "1.2.3.4"}
known_dns['chk']['test']['fwd']['host-no-reverse.example.com'] = ['1.2.3.4', 'A']
TESTS[2]['result_chk'] = {'message': 'host-no-reverse => 1.2.3.4 (TEST)', 'result': True, 'secondary': ['PROD server returns NXDOMAIN for host-no-reverse (PROD)'], 'warnings': ['REVERSE NG: got status NXDOMAIN for name 1.2.3.4 (TEST)']}

# test 3
TESTS[3] = {'hostname': "cnametestonly", 'value': "foobar"}
known_dns['chk']['test']['fwd']['cnametestonly.example.com'] = ['foobar', 'CNAME']
TESTS[3]['result_chk'] = {'message': 'cnametestonly => foobar (TEST)', 'result': True, 'secondary': ['PROD server returns NXDOMAIN for cnametestonly (PROD)'], 'warnings': []}

# test 4
TESTS[4] = {'hostname': "servfail-prod", 'value': "1.2.3.9"}
known_dns['chk']['prod']['fwd']['servfail-prod.example.com'] = ['STATUS', 'SERVFAIL']
known_dns['chk']['test']['fwd']['servfail-prod.example.com'] = ['1.2.3.9', 'A']
TESTS[4]['result_chk'] = {'message': 'prod server returned status SERVFAIL for name servfail-prod (PROD)', 'result': False, 'secondary': [], 'warnings': []}

# test 5
TESTS[5] = {'hostname': "newhostname", 'value': "1.2.3.5"}
# dns is in test 0
TESTS[5]['result_chk'] = {'message': 'newhostname resolves to 1.2.3.1 instead of 1.2.3.5 (TEST)', 'result': False, 'secondary': ['PROD server returns NXDOMAIN for newhostname (PROD)'], 'warnings': ['REVERSE NG: got status NXDOMAIN for name 1.2.3.5 (TEST)']}

# test 6
TESTS[6] = {'hostname': "newwithreverse", 'value': "1.2.3.10"}
known_dns['chk']['test']['fwd']['newwithreverse.example.com'] = ['1.2.3.10', 'A']
known_dns['chk']['test']['rev']['1.2.3.10'] = 'newwithreverse.example.com'
TESTS[6]['result_chk'] = {'message': 'newwithreverse => 1.2.3.10 (TEST)', 'result': True, 'secondary': ['PROD server returns NXDOMAIN for newwithreverse (PROD)', 'REVERSE OK: 1.2.3.10 => newwithreverse.example.com (TEST)'], 'warnings': []}

# test 7
TESTS[7] = {'hostname': "newwrongreverse", 'value': "1.2.3.11"}
known_dns['chk']['test']['fwd']['newwrongreverse.example.com'] = ['1.2.3.11', 'A']
known_dns['chk']['test']['rev']['1.2.3.11'] = 'newBADreverse.example.com'
TESTS[7]['result_chk'] = {'message': 'newwrongreverse => 1.2.3.11 (TEST)', 'result': True, 'secondary': ['PROD server returns NXDOMAIN for newwrongreverse (PROD)'], 'warnings': ['REVERSE NG: got answer newBADreverse.example.com for name 1.2.3.11 (TEST)']}

# test 8
TESTS[8] = {'hostname': "servfail-test2", 'value': "1.2.3.8"}
known_dns['chk']['test']['fwd']['servfail-test2.example.com'] = ['STATUS', 'SERVFAIL']
TESTS[8]['result_chk'] = {'message': 'status SERVFAIL for name servfail-test2 (TEST)', 'result': False, 'secondary': [], 'warnings': []}

# test 9
TESTS[9] = {'hostname': "addedhostname.example.com", 'value': "1.2.3.3"}
known_dns['ver']['test']['fwd']['addedhostname.example.com'] = ['1.2.3.3', 'A']
known_dns['ver']['prod']['fwd']['addedhostname.example.com'] = ['1.2.3.3', 'A']
TESTS[9]['result_ver'] = {'message': 'addedhostname.example.com => 1.2.3.3 (PROD)', 'result': True, 'secondary': [], 'warnings': ['REVERSE NG: got status NXDOMAIN for name 1.2.3.3 (PROD)']}

# test 10
TESTS[10] = {'hostname': "addedcname.example.com", 'value': "barbaz"}
known_dns['ver']['test']['fwd']['addedcname.example.com'] = ['barbaz', 'CNAME']
known_dns['ver']['prod']['fwd']['addedcname.example.com'] = ['barbaz', 'CNAME']
TESTS[10]['result_ver'] = {'message': 'addedcname.example.com => barbaz (PROD)', 'result': True, 'secondary': [], 'warnings': []}

# test 11
TESTS[11] = {'hostname': "addedname2.example.com", 'value': "1.2.3.12"}
known_dns['ver']['test']['fwd']['addedname2.example.com'] = ['1.2.3.12', 'A']
known_dns['ver']['prod']['fwd']['addedname2.example.com'] = ['1.2.3.13', 'A']
TESTS[11]['result_ver'] = {'message': 'addedname2.example.com resolves to 1.2.3.13 instead of 1.2.3.12 (PROD)', 'result': False, 'secondary': [], 'warnings': ['REVERSE NG: got status NXDOMAIN for name 1.2.3.12 (PROD)']}

# test 12
TESTS[12] = {'hostname': "addedwithrev.example.com", 'value': "1.2.3.16"}
known_dns['ver']['test']['fwd']['addedwithrev.example.com'] = ['1.2.3.16', 'A']
known_dns['ver']['test']['rev']['1.2.3.16'] = 'addedwithrev.example.com'
known_dns['ver']['prod']['fwd']['addedwithrev.example.com'] = ['1.2.3.16', 'A']
known_dns['ver']['prod']['rev']['1.2.3.16'] = 'addedwithrev.example.com'
TESTS[12]['result_ver'] = {'message': 'addedwithrev.example.com => 1.2.3.16 (PROD)', 'result': True, 'secondary': ['REVERSE OK: 1.2.3.16 => addedwithrev.example.com (PROD)'], 'warnings': []}

# test 13
TESTS[13] = {'hostname': "servfail-prod", 'value': "1.2.3.9"}
known_dns['ver']['prod']['fwd']['servfail-prod.example.com'] = ['STATUS', 'SERVFAIL']
TESTS[13]['result_ver'] = {'message': 'status SERVFAIL for name servfail-prod (PROD)', 'result': False, 'secondary': [], 'warnings': []}

# test 14
TESTS[14] = {'hostname': "addedbadprodrev.example.com", 'value': "1.2.3.17"}
known_dns['ver']['test']['fwd']['addedbadprodrev.example.com'] = ['1.2.3.17', 'A']
known_dns['ver']['test']['rev']['1.2.3.17'] = 'addedbadprodrev.example.com'
known_dns['ver']['prod']['fwd']['addedbadprodrev.example.com'] = ['1.2.3.17', 'A']
known_dns['ver']['prod']['rev']['1.2.3.17'] = 'groijg.example.com'
TESTS[14]['result_ver'] = {'message': 'addedbadprodrev.example.com => 1.2.3.17 (PROD)', 'result': True, 'secondary': [], 'warnings': ['REVERSE NG: got answer groijg.example.com for name 1.2.3.17 (PROD)']}

# test 15
TESTS[15] = {'hostname': "addedprodrevservfail.example.com", 'value': "1.9.9.9"}
known_dns['ver']['test']['fwd']['addedprodrevservfail.example.com'] = ['1.9.9.9', 'A']
known_dns['ver']['test']['rev']['1.9.9.9'] = 'prodrevservfail.example.com'
known_dns['ver']['prod']['fwd']['addedprodrevservfail.example.com'] = ['1.9.9.9', 'A']
known_dns['ver']['prod']['rev']['1.9.9.9'] = 'SERVFAIL'
TESTS[15]['result_ver'] = {'message': 'addedprodrevservfail.example.com => 1.9.9.9 (PROD)', 'result': True, 'secondary': [], 'warnings': ['REVERSE NG: got status SERVFAIL for name 1.9.9.9 (PROD)']}


class TestDNSCheckAdd:
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

    def test_add(self):
        """
        Run all of the tests from the TESTS dict, via yield
        """
        sc = self.setup_checks()
        sv = self.setup_verifies()
        for t in TESTS:
            tst = TESTS[t]
            if 'result_chk' in tst:
                yield "test_add chk TESTS[%d]" % t, self.dns_add, sc, tst['hostname'], tst['value'], tst['result_chk']
            if 'result_ver' in tst:
                yield "test_add ver TESTS[%d]" % t, self.dns_verify_add, sv, tst['hostname'], tst['value'], tst['result_ver']

    def dns_add(self, setup_checks, hostname, value, result):
        """
        Test checks for adding a record to DNS
        """
        foo = setup_checks.check_added_name(hostname, value)
        assert foo == result

    def dns_verify_add(self, setup_checks, hostname, value, result):
        """
        Test checks for verifying an added record
        """
        foo = setup_checks.verify_added_name(hostname, value)
        assert foo == result
