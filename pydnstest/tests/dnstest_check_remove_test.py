"""
tests for dnstest_checks.py check_removed_name() and verify_removed_name()

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

# test 0 - NXDOMAIN already
TESTS[0] = {'hostname': "badhostname"}
TESTS[0]['result_chk'] = {'message': "badhostname got status NXDOMAIN from PROD - cannot remove a name that doesn't exist (PROD)", 'secondary': [], 'result': False, 'warnings': []}

# test 1 - OK, removed from test
TESTS[1] = {'hostname': "prodonlyhostname"}
known_dns['chk']['prod']['fwd']['prodonlyhostname.example.com'] = ['1.2.3.5', 'A']
TESTS[1]['result_chk'] = {'message': 'prodonlyhostname removed, got status NXDOMAIN (TEST)', 'result': True, 'secondary': ['PROD value was 1.2.3.5 (PROD)'], 'warnings': []}

# test 2 - valid answer - not removed
TESTS[2] = {'hostname': "addedhostname"}
known_dns['chk']['prod']['fwd']['addedhostname.example.com'] = ['1.2.3.3', 'A']
known_dns['chk']['test']['fwd']['addedhostname.example.com'] = ['1.2.3.3', 'A']
known_dns['ver']['prod']['fwd']['addedhostname.example.com'] = ['1.2.3.3', 'A']
TESTS[2]['result_chk'] = {'message': "addedhostname returned valid answer of '1.2.3.3', not removed (TEST)", 'result': False, 'secondary': [], 'warnings': []}
TESTS[2]['result_ver'] = {'message': "addedhostname returned valid answer of '1.2.3.3', not removed (PROD)", 'result': False, 'secondary': [], 'warnings': []}

# test 3 - OK, removed from test, has reverse in prod too
TESTS[3] = {'hostname': "prodonlywithrev"}
known_dns['chk']['prod']['fwd']['prodonlywithrev.example.com'] = ['1.2.3.6', 'A']
known_dns['chk']['prod']['rev']['1.2.3.6'] = 'prodonlywithrev.example.com'
TESTS[3]['result_chk'] = {'message': 'prodonlywithrev removed, got status NXDOMAIN (TEST)', 'result': True, 'secondary': ['PROD value was 1.2.3.6 (PROD)'], 'warnings': []}

# test 4 - OK, removed from test, still has reverse DNS set
TESTS[4] = {'hostname': "prodwithtestrev"}
known_dns['chk']['prod']['rev']['1.2.3.7'] = 'prodwithtestrev.example.com'
known_dns['chk']['test']['rev']['1.2.3.7'] = 'prodwithtestrev.example.com'
known_dns['chk']['prod']['fwd']['prodwithtestrev.example.com'] = ['1.2.3.7', 'A']
TESTS[4]['result_chk'] = {'message': 'prodwithtestrev removed, got status NXDOMAIN (TEST)', 'result': True, 'secondary': ['PROD value was 1.2.3.7 (PROD)'], 'warnings': ['REVERSE NG: 1.2.3.7 appears to still have reverse DNS set to prodwithtestrev.example.com (TEST)']}

# test 5 - SERVFAIL
TESTS[5] = {'hostname': "servfail.example.com"}
known_dns['chk']['test']['fwd']['servfail.example.com'] = ['STATUS', 'SERVFAIL']
known_dns['chk']['prod']['fwd']['servfail.example.com'] = ['1.2.3.8', 'A']
known_dns['ver']['prod']['fwd']['servfail.example.com'] = ['STATUS', 'SERVFAIL']
TESTS[5]['result_chk'] = {'message': 'servfail.example.com returned status SERVFAIL (TEST)', 'result': False, 'secondary': [], 'warnings': []}
TESTS[5]['result_ver'] = {'message': "servfail.example.com returned status SERVFAIL (PROD)", 'result': False, 'secondary': [], 'warnings': []}

# test 6 - OK, verify - removed from both
TESTS[6] = {'hostname': "notahostname"}
TESTS[6]['result_ver'] = {'message': 'notahostname removed, got status NXDOMAIN (PROD)', 'result': True, 'secondary': [], 'warnings': []}

# test 7 - removed from prod but still there (or back again) in test
TESTS[7] = {'hostname': "newhostname"}
known_dns['ver']['test']['fwd']['newhostname.example.com'] = ['1.2.3.1', 'A']
TESTS[7]['result_ver'] = {'message': 'newhostname removed, got status NXDOMAIN (PROD)', 'result': True, 'secondary': ['newhostname returned answer 1.2.3.1 (TEST)'], 'warnings': []}

# test 8 - SERVFAIL on prod server (verify)

# test 9 - OK removal of IP (reverse DNS record)
TESTS[9] = {'hostname': "1.2.3.9"}
known_dns['chk']['prod']['rev']['1.2.3.9'] = 'test9.example.com'
TESTS[9]['result_chk'] = {'message': '1.2.3.9 removed, got status NXDOMAIN (TEST)', 'result': True, 'secondary': ['PROD value was test9.example.com (PROD)'], 'warnings': []}

# test 10 - OK verify removal of IP (reverse DNS record)
TESTS[10] = {'hostname': "1.2.3.10"}
TESTS[10]['result_ver'] = {'message': '1.2.3.10 removed, got status NXDOMAIN (PROD)', 'result': True, 'secondary': [], 'warnings': []}

# test 11 - remove name but reverse DNS points to valid A
TESTS[11] = {'hostname': 'test11a'}
known_dns['chk']['test']['fwd']['test11b.example.com'] = ['1.2.3.11', 'A']
known_dns['chk']['test']['rev']['1.2.3.11'] = 'test11b.example.com'
known_dns['chk']['prod']['fwd']['test11a.example.com'] = ['1.2.3.11', 'A']
known_dns['chk']['prod']['fwd']['test11b.example.com'] = ['1.2.3.11', 'A']
known_dns['chk']['prod']['rev']['1.2.3.11'] = 'test11b.example.com'
known_dns['ver']['test']['fwd']['test11b.example.com'] = ['1.2.3.11', 'A']
known_dns['ver']['test']['rev']['1.2.3.11'] = 'test11b.example.com'
known_dns['ver']['prod']['fwd']['test11b.example.com'] = ['1.2.3.11', 'A']
known_dns['ver']['prod']['rev']['1.2.3.11'] = 'test11b.example.com'
TESTS[11]['result_chk'] = {'message': 'test11a removed, got status NXDOMAIN (TEST)', 'result': True, 'secondary': ['PROD value was 1.2.3.11 (PROD)'], 'warnings': ['REVERSE UNKNOWN: 1.2.3.11 appears to still have reverse DNS set, but set to test11b.example.com (TEST)']}
TESTS[11]['result_ver'] = {'message': 'test11a removed, got status NXDOMAIN (PROD)', 'result': True, 'secondary': [], 'warnings': []}


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

    def test_remove(self):
        """
        Run all of the tests from the TESTS dict, via yield
        """
        sc = self.setup_checks()
        sv = self.setup_verifies()
        for t in TESTS:
            tst = TESTS[t]
            if 'result_chk' in tst:
                yield "test_remove chk TESTS[%d]" % t, self.dns_remove, sc, tst['hostname'], tst['result_chk']
            if 'result_ver' in tst:
                yield "test_remove ver TESTS[%d]" % t, self.dns_verify_remove, sv, tst['hostname'], tst['result_ver']

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
