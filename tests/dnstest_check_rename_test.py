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

# test 0
known_dns['chk']['prod']['fwd']['renametest1.example.com'] = ['1.2.3.20', 'A']
known_dns['chk']['test']['fwd']['renametest1b.example.com'] = ['1.2.3.20', 'A']
known_dns['ver']['test']['fwd']['renametest1b.example.com'] = ['1.2.3.20', 'A']
# test 1
known_dns['chk']['prod']['fwd']['renametest2.example.com'] = ['1.2.3.21', 'A']
known_dns['chk']['test']['fwd']['renametest2b.example.com'] = ['1.2.3.21', 'A']
known_dns['chk']['test']['rev']['1.2.3.21'] = 'renametest2.example.com'
known_dns['ver']['test']['fwd']['renametest2b.example.com'] = ['1.2.3.21', 'A']
# test 2
known_dns['chk']['prod']['fwd']['renametest3.example.com'] = ['1.2.3.22', 'A']
known_dns['chk']['test']['fwd']['renametest3b.example.com'] = ['1.2.3.22', 'A']
known_dns['chk']['test']['rev']['1.2.3.22'] = 'renametest3b.example.com'
known_dns['ver']['test']['fwd']['renametest3b.example.com'] = ['1.2.3.22', 'A']
# test 3
known_dns['chk']['prod']['fwd']['renametest4.example.com'] = ['1.2.3.23', 'A']
known_dns['chk']['test']['fwd']['renametest4b.example.com'] = ['1.2.3.23', 'A']
# test 4
known_dns['chk']['prod']['fwd']['renametest5.example.com'] = ['1.2.3.25', 'A']
known_dns['chk']['prod']['rev']['1.2.3.25'] = 'renametest5.example.com'
known_dns['chk']['test']['fwd']['renametest5b.example.com'] = ['1.2.3.25', 'A']
known_dns['chk']['test']['rev']['1.2.3.25'] = 'renametest5.example.com'
# test 5
known_dns['chk']['prod']['fwd']['renamedname.example.com'] = ['1.2.3.12', 'A']
known_dns['chk']['prod']['fwd']['addedname2.example.com'] = ['1.2.3.13', 'A']
known_dns['chk']['test']['fwd']['addedname2.example.com'] = ['1.2.3.12', 'A']
known_dns['ver']['prod']['fwd']['renamedname.example.com'] = ['1.2.3.12', 'A']
known_dns['ver']['prod']['fwd']['addedname2.example.com'] = ['1.2.3.13', 'A']

class TestDNSCheckRename:
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
        stub method

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
        stub method

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
        stub method

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
        stub method

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

    TESTS = [
        ("renametest1", "renametest1b", "1.2.3.20"), # 0
        ("renametest2", "renametest2b", "1.2.3.21"), # 1
        ("renametest3", "renametest3b", "1.2.3.22"), # 2
        # this next one should fail, it's actually an addition and a deletion, but values differ
        ("renametest4", "renametest4b", "1.2.3.24"), # 3
        ("renametest5", "renametest5b", "1.2.3.25"), # 4
        ]

    @pytest.mark.parametrize(("oldname", "newname", "value", "result"), [
        TESTS[0] + ({'message': 'rename renametest1 => renametest1b (TEST)', 'result': True, 'secondary': [], 'warnings': ['no reverse DNS appears to be set for 1.2.3.20 (TEST)']}, ),
        TESTS[1] + ({'message': 'rename renametest2 => renametest2b (TEST)', 'result': True, 'secondary': [], 'warnings': ['renametest2 appears to still have reverse DNS set to renametest2.example.com (TEST)']}, ),
        TESTS[2] + ({'message': 'rename renametest3 => renametest3b (TEST)', 'result': True, 'secondary': ['reverse DNS is set correctly for 1.2.3.22 (TEST)'], 'warnings': []},),
        # this next one should fail, it's actually an addition and a deletion, but values differ
        TESTS[3] + ({'message': 'renametest4 => renametest4b rename is bad, resolves to 1.2.3.23 in TEST (expected value was 1.2.3.24) (TEST)', 'result': False, 'secondary': [], 'warnings': []}, ),
        TESTS[4] + ({'message': 'rename renametest5 => renametest5b (TEST)', 'result': True, 'secondary': [], 'warnings': ['renametest5 appears to still have reverse DNS set to renametest5.example.com (TEST)']}, ),
    ])
    def test_dns_rename(self, setup_checks, oldname, newname, value, result):
        """
        Test checks for renaming a record in DNS (new name, same value)
        """
        foo = setup_checks.check_renamed_name(oldname, newname, value)
        assert foo == result

    @pytest.mark.parametrize(("oldname", "newname", "value", "result"), [
        ("addedname2", "renamedname", "1.2.3.12", {'message': 'addedname2 got answer from PROD (1.2.3.13), old name is still active (PROD)', 'result': False, 'secondary': [], 'warnings': []}),
        TESTS[4] + ({'message': 'renametest5b got status NXDOMAIN (PROD)', 'result': False, 'secondary': [], 'warnings': []}, ),
    ])
    def test_dns_verify_rename(self, setup_verifies, oldname, newname, value, result):
        """
        Test checks for verifying a renamed record in DNS (new name, same value)
        """
        foo = setup_verifies.verify_renamed_name(oldname, newname, value)
        assert foo == result
