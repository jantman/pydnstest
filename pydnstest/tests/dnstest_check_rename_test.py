"""
tests for dnstest_checks.py check_renamed_name() and verify_renamed_name()
The latest version of this package is available at:
<https://github.com/jantman/pydnstest>

##################################################################################
Copyright 2013-2017 Jason Antman <jason@jasonantman.com>

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

from pydnstest.checks import DNStestChecks
from pydnstest.config import DnstestConfig

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

# test 0 - valid rename, no reverse DNS
TESTS[0] = {'oldname': "renametest0", 'newname': "renametest0b", 'value': "1.2.3.20"}
known_dns['chk']['prod']['fwd']['renametest0.example.com'] = ['1.2.3.20', 'A']
known_dns['chk']['test']['fwd']['renametest0b.example.com'] = ['1.2.3.20', 'A']
known_dns['ver']['prod']['fwd']['renametest0b.example.com'] = ['1.2.3.20', 'A']
TESTS[0]['result_chk'] = {'message': 'rename renametest0 => renametest0b (TEST)', 'result': True, 'secondary': [], 'warnings': ['REVERSE NG: no reverse DNS appears to be set for 1.2.3.20 (TEST)']}
TESTS[0]['result_ver'] = {'message': 'rename renametest0 => renametest0b (PROD)', 'result': True, 'secondary': [], 'warnings': ['REVERSE NG: no reverse DNS appears to be set for 1.2.3.20 (PROD)']}

# test 1 - valid rename, but reverse DNS not updated (left at old value)
TESTS[1] = {'oldname': "renametest1.example.com", 'newname': "renametest1b.example.com", 'value': "1.2.3.21"}
known_dns['chk']['prod']['fwd']['renametest1.example.com'] = ['1.2.3.21', 'A']
known_dns['chk']['test']['fwd']['renametest1b.example.com'] = ['1.2.3.21', 'A']
known_dns['chk']['test']['rev']['1.2.3.21'] = 'renametest1.example.com'
known_dns['ver']['prod']['fwd']['renametest1b.example.com'] = ['1.2.3.21', 'A']
known_dns['ver']['prod']['rev']['1.2.3.21'] = 'renametest1.example.com'
TESTS[1]['result_chk'] = {'message': 'rename renametest1.example.com => renametest1b.example.com (TEST)', 'result': True, 'secondary': [], 'warnings': ['REVERSE NG: 1.2.3.21 appears to still have reverse DNS set to renametest1.example.com (TEST)']}
TESTS[1]['result_ver'] = {'message': 'rename renametest1.example.com => renametest1b.example.com (PROD)', 'result': True, 'secondary': [], 'warnings': ['REVERSE NG: 1.2.3.21 appears to still have reverse DNS set to renametest1.example.com (PROD)']}

# test 2 - everything right including reverse DNS
TESTS[2] = {'oldname': "renametest2", 'newname': "renametest2b", 'value': "1.2.3.22"}
known_dns['chk']['prod']['fwd']['renametest2.example.com'] = ['1.2.3.22', 'A']
known_dns['chk']['test']['fwd']['renametest2b.example.com'] = ['1.2.3.22', 'A']
known_dns['chk']['test']['rev']['1.2.3.22'] = 'renametest2b.example.com'
known_dns['ver']['prod']['fwd']['renametest2b.example.com'] = ['1.2.3.22', 'A']
known_dns['ver']['prod']['rev']['1.2.3.22'] = 'renametest2b.example.com'
TESTS[2]['result_chk'] = {'message': 'rename renametest2 => renametest2b (TEST)', 'result': True, 'secondary': ['REVERSE OK: reverse DNS is set correctly for 1.2.3.22 (TEST)'], 'warnings': []}
TESTS[2]['result_ver'] = {'message': 'rename renametest2 => renametest2b (PROD)', 'result': True, 'secondary': ['REVERSE OK: reverse DNS is set correctly for 1.2.3.22 (PROD)'], 'warnings': []}

# test 3 - this one should fail, it's actually an addition and a deletion, but values differ
TESTS[3] = {'oldname': "renametest3", 'newname': "renametest3b", 'value': "1.2.3.24"}
known_dns['chk']['prod']['fwd']['renametest3.example.com'] = ['1.2.3.23', 'A']
known_dns['chk']['test']['fwd']['renametest3b.example.com'] = ['1.2.3.23', 'A']
TESTS[3]['result_chk'] = {'message': 'renametest3 => renametest3b rename is bad, resolves to 1.2.3.23 in TEST (expected value was 1.2.3.24) (TEST)', 'result': False, 'secondary': [], 'warnings': []}

# test 4 - addition of new name, old name still active
TESTS[4] = {'oldname': "addedname2", 'newname': "renamedname", 'value': "1.2.3.12"}
known_dns['chk']['prod']['fwd']['renamedname.example.com'] = ['1.2.3.12', 'A']
known_dns['chk']['prod']['fwd']['addedname2.example.com'] = ['1.2.3.12', 'A']
known_dns['chk']['test']['fwd']['renamedname.example.com'] = ['1.2.3.12', 'A']
known_dns['chk']['test']['fwd']['addedname2.example.com'] = ['1.2.3.12', 'A']
known_dns['ver']['prod']['fwd']['renamedname.example.com'] = ['1.2.3.12', 'A']
known_dns['ver']['prod']['fwd']['addedname2.example.com'] = ['1.2.3.12', 'A']
TESTS[4]['result_chk'] = {'message': 'addedname2 got answer from TEST (1.2.3.12), old name is still active (TEST)', 'result': False, 'secondary': [], 'warnings': []}
TESTS[4]['result_ver'] = {'message': 'addedname2 got answer from PROD (1.2.3.12), old name is still active (PROD)', 'result': False, 'secondary': [], 'warnings': []}

# test 5 - SERVFAIL in prod
TESTS[5] = {'oldname': "renametest5", 'newname': "renametest5b", 'value': "renametest5cname"}
known_dns['chk']['prod']['fwd']['renametest5.example.com'] = ['STATUS', 'SERVFAIL']
known_dns['chk']['test']['fwd']['renametest5b.example.com'] = ['renametest5cname', 'CNAME']
known_dns['ver']['prod']['fwd']['renametest5b.example.com'] = ['STATUS', 'SERVFAIL']
TESTS[5]['result_chk'] = {'message': "renametest5 got status SERVFAIL from PROD - cannot change a name that doesn't exist (PROD)", 'result': False, 'secondary': [], 'warnings': []}
TESTS[5]['result_ver'] = {'message': "renametest5b got status SERVFAIL (PROD)", 'result': False, 'secondary': [], 'warnings': []}

# test 6 - SERVFAIL in test
TESTS[6] = {'oldname': "renametest6", 'newname': "renametest6b", 'value': "1.2.5.6"}
known_dns['chk']['prod']['fwd']['renametest6.example.com'] = ['1.2.5.6', 'A']
known_dns['chk']['test']['fwd']['renametest6b.example.com'] = ['STATUS', 'SERVFAIL']
known_dns['chk']['test']['rev']['1.2.5.6'] = 'renametest6b.example.com'
TESTS[6]['result_chk'] = {'message': "renametest6b got status SERVFAIL (TEST)", 'result': False, 'secondary': [], 'warnings': []}

# test 7 - valid but different answers in test and prod
TESTS[7] = {'oldname': "renametest7", 'newname': "renametest7b", 'value': '1.2.5.7'}
known_dns['chk']['test']['fwd']['renametest7b.example.com'] = ['1.2.5.7', 'A']
known_dns['chk']['prod']['fwd']['renametest7.example.com'] = ['1.2.4.7', 'A']
known_dns['ver']['test']['fwd']['renametest7b.example.com'] = ['1.2.5.7', 'A']
known_dns['ver']['prod']['fwd']['renametest7b.example.com'] = ['1.2.4.7', 'A']
TESTS[7]['result_chk'] = {'message': 'renametest7 => renametest7b rename is bad, resolves to 1.2.5.7 in TEST and 1.2.4.7 in PROD', 'result': False, 'secondary': [], 'warnings': []}
TESTS[7]['result_ver'] = {'message': 'renametest7 => renametest7b rename is bad, resolves to 1.2.5.7 in PROD (expected value was 1.2.5.7) (PROD)', 'result': False, 'secondary': [], 'warnings': []}

# test 8 - valid rename, is a CNAME
TESTS[8] = {'oldname': "renametest8", 'newname': "renametest8b", 'value': "renametest8cname"}
known_dns['chk']['prod']['fwd']['renametest8.example.com'] = ['renametest8cname', 'CNAME']
known_dns['chk']['test']['fwd']['renametest8b.example.com'] = ['renametest8cname', 'CNAME']
known_dns['ver']['prod']['fwd']['renametest8b.example.com'] = ['renametest8cname', 'CNAME']
TESTS[8]['result_chk'] = {'message': 'rename renametest8 => renametest8b (TEST)', 'result': True, 'secondary': [], 'warnings': []}
TESTS[8]['result_ver'] = {'message': 'rename renametest8 => renametest8b (PROD)', 'result': True, 'secondary': [], 'warnings': []}


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
        DNS stub method

        return a dict that looks like the return value from pydnstest.resolve_name
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

        return a dict that looks like the return value from pydnstest.lookup_reverse
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

        return a dict that looks like the return value from pydnstest.resolve_name
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

        return a dict that looks like the return value from pydnstest.lookup_reverse
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

    def test_rename(self):
        """
        Run all of the tests from the TESTS dict, via yield
        """
        sc = self.setup_checks()
        sv = self.setup_verifies()
        for t in TESTS:
            tst = TESTS[t]
            if 'result_chk' in tst:
                yield "test_rename chk TESTS[%d]" % t, self.dns_rename, sc, tst['oldname'], tst['newname'], tst['value'], tst['result_chk']
            if 'result_ver' in tst:
                yield "test_rename ver TESTS[%d]" % t, self.dns_verify_rename, sv, tst['oldname'], tst['newname'], tst['value'], tst['result_ver']

    def dns_rename(self, setup_checks, oldname, newname, value, result):
        """
        Test checks for renaming a record in DNS (new name, same value)
        """
        foo = setup_checks.check_renamed_name(oldname, newname, value)
        assert foo == result

    def dns_verify_rename(self, setup_verifies, oldname, newname, value, result):
        """
        Test checks for verifying a renamed record in DNS (new name, same value)
        """
        foo = setup_verifies.verify_renamed_name(oldname, newname, value)
        assert foo == result
