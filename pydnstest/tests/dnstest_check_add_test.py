"""
tests for dnstest_checks.py check_added_name() and verify_added_name()

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

# test 0 - OK but no reverse
TESTS[0] = {'hostname': "newhostname", 'value': "1.2.3.1"}
known_dns['chk']['test']['fwd']['newhostname.example.com'] = ['1.2.3.1', 'A']
known_dns['ver']['test']['fwd']['newhostname.example.com'] = ['1.2.3.1', 'A']
known_dns['ver']['prod']['fwd']['newhostname.example.com'] = ['1.2.3.1', 'A']
TESTS[0]['result_chk'] = {'message': 'newhostname => 1.2.3.1 (TEST)', 'result': True, 'secondary': ['PROD server returns NXDOMAIN for newhostname (PROD)'], 'warnings': ['REVERSE NG: got status NXDOMAIN for name 1.2.3.1 (TEST)']}
TESTS[0]['result_ver'] = {'message': 'newhostname => 1.2.3.1 (PROD)', 'result': True, 'secondary': [], 'warnings': ['REVERSE NG: got status NXDOMAIN for name 1.2.3.1 (PROD)']}

# test 1 - already in prod
TESTS[1] = {'hostname': "existinghostname", 'value': "1.2.3.2"}
known_dns['chk']['prod']['fwd']['existinghostname.example.com'] = ['1.2.3.2', 'A']
TESTS[1]['result_chk'] = {'message': 'new name existinghostname returned valid result from prod server (PROD)', 'result': False, 'secondary': [], 'warnings': []}

# test 2 - OK, cname
TESTS[2] = {'hostname': "cnametestonly", 'value': "foobar"}
known_dns['chk']['test']['fwd']['cnametestonly.example.com'] = ['foobar', 'CNAME']
known_dns['ver']['test']['fwd']['cnametestonly.example.com'] = ['foobar', 'CNAME']
known_dns['ver']['prod']['fwd']['cnametestonly.example.com'] = ['foobar', 'CNAME']
TESTS[2]['result_chk'] = {'message': 'cnametestonly => foobar (TEST)', 'result': True, 'secondary': ['PROD server returns NXDOMAIN for cnametestonly (PROD)'], 'warnings': []}
TESTS[2]['result_ver'] = {'message': 'cnametestonly => foobar (PROD)', 'result': True, 'secondary': [], 'warnings': []}

# test 3 - SERVFAIL in prod
TESTS[3] = {'hostname': "servfail-prod", 'value': "1.2.3.9"}
known_dns['chk']['prod']['fwd']['servfail-prod.example.com'] = ['STATUS', 'SERVFAIL']
known_dns['chk']['test']['fwd']['servfail-prod.example.com'] = ['1.2.3.9', 'A']
TESTS[3]['result_chk'] = {'message': 'prod server returned status SERVFAIL for name servfail-prod (PROD)', 'result': False, 'secondary': [], 'warnings': []}

# test 4 - wrong value, no reverse
TESTS[4] = {'hostname': "addtest4", 'value': "1.2.3.5"}
known_dns['chk']['test']['fwd']['addtest4.example.com'] = ['1.2.3.1', 'A']
known_dns['ver']['test']['fwd']['addtest4.example.com'] = ['1.2.3.1', 'A']
known_dns['ver']['prod']['fwd']['addtest4.example.com'] = ['1.2.3.1', 'A']
known_dns['ver']['test']['fwd']['addtest4.example.com'] = ['1.2.3.5', 'A']
known_dns['ver']['prod']['fwd']['addtest4.example.com'] = ['1.2.3.13', 'A']
TESTS[4]['result_chk'] = {'message': 'addtest4 resolves to 1.2.3.1 instead of 1.2.3.5 (TEST)', 'result': False, 'secondary': ['PROD server returns NXDOMAIN for addtest4 (PROD)'], 'warnings': ['REVERSE NG: got status NXDOMAIN for name 1.2.3.5 (TEST)']}
TESTS[4]['result_ver'] = {'message': 'addtest4 resolves to 1.2.3.13 instead of 1.2.3.5 (PROD)', 'result': False, 'secondary': [], 'warnings': ['REVERSE NG: got status NXDOMAIN for name 1.2.3.5 (PROD)']}

# test 5 - OK, with reverse
TESTS[5] = {'hostname': "newwithreverse.example.com", 'value': "1.2.3.10"}
known_dns['chk']['test']['fwd']['newwithreverse.example.com'] = ['1.2.3.10', 'A']
known_dns['chk']['test']['rev']['1.2.3.10'] = 'newwithreverse.example.com'
known_dns['ver']['test']['fwd']['newwithreverse.example.com'] = ['1.2.3.10', 'A']
known_dns['ver']['test']['rev']['1.2.3.10'] = 'newwithreverse.example.com'
known_dns['ver']['prod']['fwd']['newwithreverse.example.com'] = ['1.2.3.10', 'A']
known_dns['ver']['prod']['rev']['1.2.3.10'] = 'newwithreverse.example.com'
TESTS[5]['result_chk'] = {'message': 'newwithreverse.example.com => 1.2.3.10 (TEST)', 'result': True, 'secondary': ['PROD server returns NXDOMAIN for newwithreverse.example.com (PROD)', 'REVERSE OK: 1.2.3.10 => newwithreverse.example.com (TEST)'], 'warnings': []}
TESTS[5]['result_ver'] = {'message': 'newwithreverse.example.com => 1.2.3.10 (PROD)', 'result': True, 'secondary': ['REVERSE OK: 1.2.3.10 => newwithreverse.example.com (PROD)'], 'warnings': []}

# test 7 - OK, but bad reverse record
TESTS[6] = {'hostname': "newwrongreverse", 'value': "1.2.3.11"}
known_dns['chk']['test']['fwd']['newwrongreverse.example.com'] = ['1.2.3.11', 'A']
known_dns['chk']['test']['rev']['1.2.3.11'] = 'newBADreverse.example.com'
known_dns['ver']['test']['fwd']['newwrongreverse.example.com'] = ['1.2.3.11', 'A']
known_dns['ver']['test']['rev']['1.2.3.11'] = 'newwrongreverse.example.com'
known_dns['ver']['prod']['fwd']['newwrongreverse.example.com'] = ['1.2.3.11', 'A']
known_dns['ver']['prod']['rev']['1.2.3.11'] = 'groijg.example.com'
TESTS[6]['result_chk'] = {'message': 'newwrongreverse => 1.2.3.11 (TEST)', 'result': True, 'secondary': ['PROD server returns NXDOMAIN for newwrongreverse (PROD)'], 'warnings': ['REVERSE NG: got answer newBADreverse.example.com for name 1.2.3.11 (TEST)']}
TESTS[6]['result_ver'] = {'message': 'newwrongreverse => 1.2.3.11 (PROD)', 'result': True, 'secondary': [], 'warnings': ['REVERSE NG: got answer groijg.example.com for name 1.2.3.11 (PROD)']}

# test 7 - SERVFAIL for test
TESTS[7] = {'hostname': "servfail-test2", 'value': "1.2.3.8"}
known_dns['chk']['test']['fwd']['servfail-test2.example.com'] = ['STATUS', 'SERVFAIL']
TESTS[7]['result_chk'] = {'message': 'status SERVFAIL for name servfail-test2 (TEST)', 'result': False, 'secondary': [], 'warnings': []}

# test 8 - SERVFAIL in prod
TESTS[8] = {'hostname': "servfail-prod", 'value': "1.2.3.9"}
known_dns['ver']['prod']['fwd']['servfail-prod.example.com'] = ['STATUS', 'SERVFAIL']
TESTS[8]['result_ver'] = {'message': 'status SERVFAIL for name servfail-prod (PROD)', 'result': False, 'secondary': [], 'warnings': []}

# test 9 - OK but SERVFAIL for reverse
TESTS[9] = {'hostname': "addedprodrevservfail.example.com", 'value': "1.9.9.9"}
known_dns['ver']['test']['fwd']['addedprodrevservfail.example.com'] = ['1.9.9.9', 'A']
known_dns['ver']['test']['rev']['1.9.9.9'] = 'prodrevservfail.example.com'
known_dns['ver']['prod']['fwd']['addedprodrevservfail.example.com'] = ['1.9.9.9', 'A']
known_dns['ver']['prod']['rev']['1.9.9.9'] = 'SERVFAIL'
TESTS[9]['result_ver'] = {'message': 'addedprodrevservfail.example.com => 1.9.9.9 (PROD)', 'result': True, 'secondary': [], 'warnings': ['REVERSE NG: got status SERVFAIL for name 1.9.9.9 (PROD)']}


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
