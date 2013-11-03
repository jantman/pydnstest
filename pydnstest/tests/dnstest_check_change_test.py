"""
tests for dnstest_checks.py check_changed_name() and verify_changed_name()

The latest version of this package is available at:
<https://github.com/jantman/pydnstest>

##################################################################################
Copyright 2013 Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>

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

# test 0 - change OK but no reverse DNS set
TESTS[0] = {"hostname": "addedname2.example.com", "newvalue": "1.2.3.12"}
known_dns['chk']['test']['fwd']['addedname2.example.com'] = ['1.2.3.12', 'A']
known_dns['chk']['prod']['fwd']['addedname2.example.com'] = ['1.2.3.13', 'A']
known_dns['ver']['test']['fwd']['addedname2.example.com'] = ['1.2.3.12', 'A']
known_dns['ver']['prod']['fwd']['addedname2.example.com'] = ['1.2.3.12', 'A']
TESTS[0]['result_chk'] = {'message': "change addedname2.example.com from '1.2.3.13' to '1.2.3.12' (TEST)", 'result': True, 'secondary': [], 'warnings': ['REVERSE NG: no reverse DNS appears to be set for 1.2.3.12 (TEST)']}
TESTS[0]['result_ver'] = {'message': "change addedname2.example.com value to '1.2.3.12' (PROD)", 'result': True, 'secondary': [], 'warnings': ['REVERSE NG: no reverse DNS appears to be set for 1.2.3.12 (PROD)']}

# test 1 - change value of a CNAME; change to invalid value, test fails
TESTS[1] = {'hostname': 'changetest1', 'newvalue': 'changetest1val'}
known_dns['chk']['test']['fwd']['changetest1.example.com'] = ['changetest1bad.example.com', 'CNAME']
known_dns['chk']['prod']['fwd']['changetest1.example.com'] = ['changetest1orig.example.com', 'CNAME']
known_dns['ver']['test']['fwd']['changetest1.example.com'] = ['changetest1bad.example.com', 'CNAME']
known_dns['ver']['prod']['fwd']['changetest1.example.com'] = ['changetest1bad.example.com', 'CNAME']
TESTS[1]['result_chk'] = {'message': 'changetest1 resolves to changetest1bad.example.com instead of changetest1val (TEST)', 'result': False, 'secondary': [], 'warnings': []}
TESTS[1]['result_ver'] = {'message': 'changetest1 resolves to changetest1bad.example.com instead of changetest1val (PROD)', 'result': False, 'secondary': [], 'warnings': []}

# test 2 - SERVFAIL
TESTS[2] = {'hostname': 'changetest2', 'newvalue': 'changetest2val'}
known_dns['chk']['test']['fwd']['changetest2.example.com'] = ['STATUS', 'SERVFAIL']
known_dns['chk']['prod']['fwd']['changetest2.example.com'] = ['changetest2orig.example.com', 'CNAME']
known_dns['ver']['test']['fwd']['changetest2.example.com'] = ['changetest2orig.example.com', 'CNAME']
known_dns['ver']['prod']['fwd']['changetest2.example.com'] = ['STATUS', 'SERVFAIL']
TESTS[2]['result_chk'] = {'message': 'changetest2 got status SERVFAIL (TEST)', 'result': False, 'secondary': [], 'warnings': []}
TESTS[2]['result_ver'] = {'message': 'changetest2 got status SERVFAIL from PROD (PROD)', 'result': False, 'secondary': [], 'warnings': []}

# test 3 - SERVFAIL in prod only
TESTS[3] = {'hostname': 'changetest3', 'newvalue': '1.2.8.3'}
known_dns['chk']['test']['fwd']['changetest3.example.com'] = ['1.2.8.3', 'A']
known_dns['chk']['prod']['fwd']['changetest3.example.com'] = ['STATUS', 'SERVFAIL']
TESTS[3]['result_chk'] = {'message': "changetest3 got status SERVFAIL from PROD - cannot change a name that doesn't exist (PROD)", 'result': False, 'secondary': [], 'warnings': []}

# test 4 - not changed, same value in test and prod
TESTS[4] = {'hostname': 'changetest4', 'newvalue': '1.2.8.4'}
known_dns['chk']['test']['fwd']['changetest4.example.com'] = ['1.2.8.3', 'A']
known_dns['chk']['prod']['fwd']['changetest4.example.com'] = ['1.2.8.3', 'A']
TESTS[4]['result_chk'] = {'message': "changetest4 is not changed, resolves to same value (1.2.8.3) in TEST and PROD", 'result': False, 'secondary': [], 'warnings': []}

# test 5 - change OK and reverse set
TESTS[5] = {"hostname": "changetest5", "newvalue": "1.2.3.5"}
known_dns['chk']['test']['fwd']['changetest5.example.com'] = ['1.2.3.5', 'A']
known_dns['chk']['test']['rev']['1.2.3.5'] = 'changetest5.example.com'
known_dns['chk']['prod']['fwd']['changetest5.example.com'] = ['1.2.3.96', 'A']
known_dns['ver']['test']['fwd']['changetest5.example.com'] = ['1.2.3.5', 'A']
known_dns['ver']['test']['rev']['1.2.3.5'] = 'changetest5.example.com'
known_dns['ver']['prod']['fwd']['changetest5.example.com'] = ['1.2.3.5', 'A']
known_dns['ver']['prod']['rev']['1.2.3.5'] = 'changetest5.example.com'
TESTS[5]['result_chk'] = {'message': "change changetest5 from '1.2.3.96' to '1.2.3.5' (TEST)", 'result': True, 'secondary': ['REVERSE OK: 1.2.3.5 => changetest5.example.com (TEST)'], 'warnings': []}
TESTS[5]['result_ver'] = {'message': "change changetest5 value to '1.2.3.5' (PROD)", 'result': True, 'secondary': ['REVERSE OK: 1.2.3.5 => changetest5.example.com (PROD)'], 'warnings': []}

# test 6 - change OK but reverse set to old value
TESTS[6] = {"hostname": "changetest6", "newvalue": "1.2.3.6"}
known_dns['chk']['test']['fwd']['changetest6.example.com'] = ['1.2.3.6', 'A']
known_dns['chk']['test']['rev']['1.2.3.96'] = 'changetest6.example.com'
known_dns['chk']['prod']['fwd']['changetest6.example.com'] = ['1.2.3.96', 'A']
known_dns['ver']['test']['fwd']['changetest6.example.com'] = ['1.2.3.6', 'A']
known_dns['ver']['test']['rev']['1.2.3.96'] = 'changetest6.example.com'
known_dns['ver']['prod']['fwd']['changetest6.example.com'] = ['1.2.3.6', 'A']
known_dns['ver']['prod']['rev']['1.2.3.96'] = 'changetest6.example.com'
TESTS[6]['result_chk'] = {'message': "change changetest6 from '1.2.3.96' to '1.2.3.6' (TEST)", 'result': True, 'secondary': [], 'warnings': ['REVERSE NG: no reverse DNS appears to be set for 1.2.3.6 (TEST)']}
TESTS[6]['result_ver'] = {'message': "change changetest6 value to '1.2.3.6' (PROD)", 'result': True, 'secondary': [], 'warnings': ['REVERSE NG: no reverse DNS appears to be set for 1.2.3.6 (PROD)']}

# test 7 - change OK but reverse set to another name
TESTS[7] = {"hostname": "changetest7", "newvalue": "1.2.3.7"}
known_dns['chk']['test']['fwd']['changetest7.example.com'] = ['1.2.3.7', 'A']
known_dns['chk']['test']['rev']['1.2.3.7'] = 'changetest7bad.example.com'
known_dns['chk']['prod']['fwd']['changetest7.example.com'] = ['1.2.3.97', 'A']
known_dns['ver']['test']['fwd']['changetest7.example.com'] = ['1.2.3.7', 'A']
known_dns['ver']['test']['rev']['1.2.3.7'] = 'changetest7bad.example.com'
known_dns['ver']['prod']['fwd']['changetest7.example.com'] = ['1.2.3.7', 'A']
known_dns['ver']['prod']['rev']['1.2.3.7'] = 'changetest7bad.example.com'
TESTS[7]['result_chk'] = {'message': "change changetest7 from '1.2.3.97' to '1.2.3.7' (TEST)", 'result': True, 'secondary': [], 'warnings': ['REVERSE NG: 1.2.3.7 appears to still have reverse DNS set to changetest7bad.example.com (TEST)']}
TESTS[7]['result_ver'] = {'message': "change changetest7 value to '1.2.3.7' (PROD)", 'result': True, 'secondary': [], 'warnings': ['REVERSE NG: 1.2.3.7 appears to still have reverse DNS set to changetest7bad.example.com (PROD)']}

# test 8 - SERVFAIL in test only, during verification only
TESTS[8] = {'hostname': 'changetest8', 'newvalue': 'changetest8val'}
known_dns['ver']['prod']['fwd']['changetest8.example.com'] = ['changetest8orig.example.com', 'CNAME']
known_dns['ver']['test']['fwd']['changetest8.example.com'] = ['STATUS', 'SERVFAIL']
TESTS[8]['result_ver'] = {'message': 'changetest8 got status SERVFAIL (TEST)', 'result': False, 'secondary': [], 'warnings': []}

# test 9 - change OK but no reverse DNS set; change A to CNAME
TESTS[9] = {"hostname": "changetest9.example.com", "newvalue": "changetest9cname.example.com"}
known_dns['chk']['test']['fwd']['changetest9.example.com'] = ['changetest9cname.example.com', 'CNAME']
known_dns['chk']['prod']['fwd']['changetest9.example.com'] = ['1.2.3.13', 'A']
known_dns['ver']['test']['fwd']['changetest9.example.com'] = ['changetest9cname.example.com', 'CNAME']
known_dns['ver']['prod']['fwd']['changetest9.example.com'] = ['changetest9cname.example.com', 'CNAME']
TESTS[9]['result_chk'] = {'message': "change changetest9.example.com from '1.2.3.13' to 'changetest9cname.example.com' (TEST)", 'result': True, 'secondary': [], 'warnings': []}
TESTS[9]['result_ver'] = {'message': "change changetest9.example.com value to 'changetest9cname.example.com' (PROD)", 'result': True, 'secondary': [], 'warnings': []}


class TestDNSCheckChange:
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

    def test_change(self):
        """
        Run all of the tests from the TESTS dict, via yield
        """
        sc = self.setup_checks()
        sv = self.setup_verifies()
        for t in TESTS:
            tst = TESTS[t]
            if 'result_chk' in tst:
                yield "test_change chk TESTS[%d]" % t, self.dns_change, sc, tst['hostname'], tst['newvalue'], tst['result_chk']
            if 'result_ver' in tst:
                yield "test_change ver TESTS[%d]" % t, self.dns_verify_change, sv, tst['hostname'], tst['newvalue'], tst['result_ver']

    def dns_change(self, setup_checks, hostname, newval, result):
        """
        Test checks for changing a record in DNS (same name, new value)
        """
        foo = setup_checks.check_changed_name(hostname, newval)
        assert foo == result

    def dns_verify_change(self, setup_checks, hostname, newval, result):
        """
        Test checks for verifying a changed record in DNS (same name, new value)
        """
        foo = setup_checks.verify_changed_name(hostname, newval)
        assert foo == result
