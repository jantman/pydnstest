# tests for dns_parser.py

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../')

from dnstest_checks import DNStestChecks
from dnstest_config import DnstestConfig


# dict of known (mocked) reverse DNS values for test and prod servers
known_rev_dns = {'test_server_stub': {}, 'prod_server_stub': {}}
known_rev_dns['prod_server_stub']['1.2.3.6'] = 'prodonlywithrev.example.com'
known_rev_dns['prod_server_stub']['1.2.3.7'] = 'prodwithtestrev.example.com'
known_rev_dns['prod_server_stub']['1.2.3.15'] = 'addedname3.example.com'
known_rev_dns['prod_server_stub']['1.2.3.16'] = 'addedwithrev.example.com'
known_rev_dns['prod_server_stub']['1.2.3.17'] = 'groijg.example.com'

known_rev_dns['test_server_stub']['10.188.12.10'] = 'foo.example.com'
known_rev_dns['test_server_stub']['1.2.3.7'] = 'prodwithtestrev.example.com'
known_rev_dns['test_server_stub']['1.2.3.10'] = 'newwithreverse.example.com'
known_rev_dns['test_server_stub']['1.2.3.11'] = 'newBADreverse.example.com'
known_rev_dns['test_server_stub']['1.2.3.15'] = 'addedname3.example.com'
known_rev_dns['test_server_stub']['1.2.3.16'] = 'addedwithrev.example.com'
known_rev_dns['test_server_stub']['1.2.3.17'] = 'addedbadprodrev.example.com'
known_rev_dns['test_server_stub']['1.9.9.9'] = 'prodrevservfail.example.com'
known_rev_dns['test_server_stub']['1.2.3.21'] = 'renametest2.example.com'
known_rev_dns['test_server_stub']['1.2.3.22'] = 'renametest3b.example.com'

# dict of known (mocked) forward DNS values for test and prod servers
# each known_dns[server][name] is [value, record_type]
known_dns = {'test_server_stub': {}, 'prod_server_stub': {}}
known_dns['prod_server_stub']['existinghostname.example.com'] = ['1.2.3.2', 'A']
known_dns['prod_server_stub']['addedhostname.example.com'] = ['1.2.3.3', 'A']
known_dns['prod_server_stub']['prodonlyhostname.example.com'] = ['1.2.3.5', 'A']
known_dns['prod_server_stub']['prodonlywithrev.example.com'] = ['1.2.3.6', 'A']
known_dns['prod_server_stub']['prodwithtestrev.example.com'] = ['1.2.3.7', 'A']
known_dns['prod_server_stub']['servfail-test.example.com'] = ['1.2.3.8', 'A']
known_dns['prod_server_stub']['addedcname.example.com'] = ['barbaz', 'CNAME']
known_dns['prod_server_stub']['addedname2.example.com'] = ['1.2.3.13', 'A']
known_dns['prod_server_stub']['addedname3.example.com'] = ['1.2.3.14', 'A']
known_dns['prod_server_stub']['addedwithrev.example.com'] = ['1.2.3.16', 'A']
known_dns['prod_server_stub']['addedbadprodrev.example.com'] = ['1.2.3.17', 'A']
known_dns['prod_server_stub']['addedprodrevservfail.example.com'] = ['1.9.9.9', 'A']
known_dns['prod_server_stub']['renametest1.example.com'] = ['1.2.3.20', 'A']
known_dns['prod_server_stub']['renametest2.example.com'] = ['1.2.3.21', 'A']
known_dns['prod_server_stub']['renametest3.example.com'] = ['1.2.3.22', 'A']

known_dns['test_server_stub']['newhostname.example.com'] = ['1.2.3.1', 'A']
known_dns['test_server_stub']['addedhostname.example.com'] = ['1.2.3.3', 'A']
known_dns['test_server_stub']['host-no-reverse.example.com'] = ['1.2.3.4', 'A']
known_dns['test_server_stub']['servfail-prod.example.com'] = ['1.2.3.9', 'A']
known_dns['test_server_stub']['cnametestonly.example.com'] = ['foobar', 'CNAME']
known_dns['test_server_stub']['newwithreverse.example.com'] = ['1.2.3.10', 'A']
known_dns['test_server_stub']['newwrongreverse.example.com'] = ['1.2.3.11', 'A']
known_dns['test_server_stub']['addedcname.example.com'] = ['barbaz', 'CNAME']
known_dns['test_server_stub']['addedname2.example.com'] = ['1.2.3.12', 'A']
known_dns['test_server_stub']['addedname3.example.com'] = ['1.2.3.15', 'A']
known_dns['test_server_stub']['addedwithrev.example.com'] = ['1.2.3.16', 'A']
known_dns['test_server_stub']['addedbadprodrev.example.com'] = ['1.2.3.17', 'A']
known_dns['test_server_stub']['addedprodrevservfail.example.com'] = ['1.9.9.9', 'A']
known_dns['test_server_stub']['renametest1b.example.com'] = ['1.2.3.20', 'A']
known_dns['test_server_stub']['renametest2b.example.com'] = ['1.2.3.21', 'A']
known_dns['test_server_stub']['renametest3b.example.com'] = ['1.2.3.22', 'A']


class TestDNSChecks:
    """
    Test DNS checks, using stubbed name resolution methods that return static values.

    The code in this class checks the logic of dnstest.py's test_*_name methods, which take
    input describing the change, and query nameservers to check current prod and staging status.
    """

    @pytest.fixture(scope="module")
    def setup_checks(self):
        config = DnstestConfig()
        config.server_test = "test_server_stub"
        config.server_prod = "prod_server_stub"
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
        stub method

        return a dict that looks like the return value from dnstest.resolve_name
        but either returns one of a hard-coded group of dicts, or an error.
        """

        if query in known_dns[to_server]:
            return {'answer': {'name': query, 'data': known_dns[to_server][query][0], 'typename': known_dns[to_server][query][1], 'classstr': 'IN', 'ttl': 360, 'type': 5, 'class': 1, 'rdlength': 14}}
        elif (query == "servfail-prod" or query == "servfail-prod.example.com") and to_server == 'prod_server_stub':
            return {'status': 'SERVFAIL'}
        elif (query == "servfail-test" or query == "servfail-test.example.com" or query == "servfail-test2" or query == "servfail-test2.example.com") and to_server == 'test_server_stub':
            return {'status': 'SERVFAIL'}
        elif (query == "servall-test" or query == "servfail-all.example.com"):
            return {'status': 'SERVFAIL'}
        else:
            return {'status': 'NXDOMAIN'}

    def stub_lookup_reverse(self, name, to_server, to_port=53):
        """
        stub method

        return a dict that looks like the return value from dnstest.lookup_reverse
        but either returns one of a hard-coded group of dicts, or an error.
        """

        if name in known_rev_dns[to_server]:
            return {'answer': {'name': name, 'data': known_rev_dns[to_server][name], 'typename': 'PTR', 'classstr': 'IN', 'ttl': 360, 'type': 12, 'class': 1, 'rdlength': 33}}
        elif name in '1.9.9.9' and to_server == 'prod_server_stub':
            return {'status': 'SERVFAIL'}
        else:
            return {'status': 'NXDOMAIN'}

    ###########################################
    # Done with setup, start the actual tests #
    ###########################################

    @pytest.mark.parametrize(("hostname", "value", "result"), [
        ("newhostname", "1.2.3.1", {'message': 'newhostname => 1.2.3.1 (TEST)', 'result': True, 'secondary': ['PROD server returns NXDOMAIN for newhostname (PROD)'], 'warnings': ['REVERSE NG: got status NXDOMAIN for name 1.2.3.1 (TEST)']}),
        ("existinghostname", "1.2.3.2", {'message': 'new name existinghostname returned valid result from prod server (PROD)', 'result': False, 'secondary': [], 'warnings': []}),
        ("host-no-reverse", "1.2.3.4", {'message': 'host-no-reverse => 1.2.3.4 (TEST)', 'result': True, 'secondary': ['PROD server returns NXDOMAIN for host-no-reverse (PROD)'], 'warnings': ['REVERSE NG: got status NXDOMAIN for name 1.2.3.4 (TEST)']}),
        ("cnametestonly", "foobar", {'message': 'cnametestonly => foobar (TEST)', 'result': True, 'secondary': ['PROD server returns NXDOMAIN for cnametestonly (PROD)'], 'warnings': []}),
        ("servfail-prod", "1.2.3.9", {'message': 'prod server returned status SERVFAIL for name servfail-prod (PROD)', 'result': False, 'secondary': [], 'warnings': []}),
        ("newhostname", "1.2.3.5", {'message': 'newhostname resolves to 1.2.3.1 instead of 1.2.3.5 (TEST)', 'result': False, 'secondary': ['PROD server returns NXDOMAIN for newhostname (PROD)'], 'warnings': ['REVERSE NG: got status NXDOMAIN for name 1.2.3.5 (TEST)']}),
        ("newwithreverse", "1.2.3.10", {'message': 'newwithreverse => 1.2.3.10 (TEST)', 'result': True, 'secondary': ['PROD server returns NXDOMAIN for newwithreverse (PROD)', 'REVERSE OK: 1.2.3.10 => newwithreverse.example.com (TEST)'], 'warnings': []}),
        ("newwrongreverse", "1.2.3.11", {'message': 'newwrongreverse => 1.2.3.11 (TEST)', 'result': True, 'secondary': ['PROD server returns NXDOMAIN for newwrongreverse (PROD)'], 'warnings': ['REVERSE NG: got answer newBADreverse.example.com for name 1.2.3.11 (TEST)']}),
        ("servfail-test2", "1.2.3.8", {'message': 'status SERVFAIL for name servfail-test2 (TEST)', 'result': False, 'secondary': [], 'warnings': []}),
    ])
    def test_dns_add(self, setup_checks, hostname, value, result):
        """
        Test checks for adding a record to DNS
        """
        foo = setup_checks.check_added_name(hostname, value)
        assert foo == result

    @pytest.mark.parametrize(("hostname", "value", "result"), [
        ("addedhostname.example.com", "1.2.3.3", {'message': 'addedhostname.example.com => 1.2.3.3 (PROD)', 'result': True, 'secondary': [], 'warnings': ['REVERSE NG: got status NXDOMAIN for name 1.2.3.3 (PROD)']}),
        ("addedcname.example.com", "barbaz", {'message': 'addedcname.example.com => barbaz (PROD)', 'result': True, 'secondary': [], 'warnings': []}),
        ("addedname2.example.com", "1.2.3.12", {'message': 'addedname2.example.com resolves to 1.2.3.13 instead of 1.2.3.12 (PROD)', 'result': False, 'secondary': [], 'warnings': ['REVERSE NG: got status NXDOMAIN for name 1.2.3.12 (PROD)']}),
        ("addedwithrev.example.com", "1.2.3.16", {'message': 'addedwithrev.example.com => 1.2.3.16 (PROD)', 'result': True, 'secondary': ['REVERSE OK: 1.2.3.16 => addedwithrev.example.com (PROD)'], 'warnings': []}),
        ("servfail-prod", "1.2.3.9", {'message': 'status SERVFAIL for name servfail-prod (PROD)', 'result': False, 'secondary': [], 'warnings': []}),
        ("addedbadprodrev.example.com", "1.2.3.17", {'message': 'addedbadprodrev.example.com => 1.2.3.17 (PROD)', 'result': True, 'secondary': [], 'warnings': ['REVERSE NG: got answer groijg.example.com for name 1.2.3.17 (PROD)']}),
        ("addedprodrevservfail.example.com", "1.9.9.9", {'message': 'addedprodrevservfail.example.com => 1.9.9.9 (PROD)', 'result': True, 'secondary': [], 'warnings': ['REVERSE NG: got status SERVFAIL for name 1.9.9.9 (PROD)']}),
    ])
    def test_dns_verify_add(self, setup_checks, hostname, value, result):
        """
        Test checks for verifying an added record
        """
        foo = setup_checks.verify_added_name(hostname, value)
        assert foo == result

    @pytest.mark.parametrize(("hostname", "result"), [
        ("badhostname", {'message': "badhostname got status NXDOMAIN from PROD - cannot remove a name that doesn't exist (PROD)", 'secondary': [], 'result': False, 'warnings': []}),
        ("prodonlyhostname", {'message': 'prodonlyhostname removed, got status NXDOMAIN (TEST)', 'result': True, 'secondary': ['PROD value was 1.2.3.5 (PROD)'], 'warnings': []}),
        ("addedhostname", {'message': 'addedhostname returned valid answer, not removed (TEST)', 'result': False, 'secondary': [], 'warnings': []}),
        ("prodonlywithrev", {'message': 'prodonlywithrev removed, got status NXDOMAIN (TEST)', 'result': True, 'secondary': ['PROD value was 1.2.3.6 (PROD)'], 'warnings': []}),
        ("prodwithtestrev", {'message': 'prodwithtestrev removed, got status NXDOMAIN (TEST)', 'result': True, 'secondary': ['PROD value was 1.2.3.7 (PROD)'], 'warnings': ['prodwithtestrev appears to still have reverse DNS set to prodwithtestrev.example.com (TEST)']}),
        ("servfail-test", {'message': 'servfail-test returned status SERVFAIL (TEST)', 'result': False, 'secondary': [], 'warnings': []}),
    ])
    def test_dns_remove(self, setup_checks, hostname, result):
        """
        Test checks for removing a record from DNS
        """
        foo = setup_checks.check_removed_name(hostname)
        assert foo == result

    @pytest.mark.parametrize(("hostname", "result"), [
        ("notahostname", {'message': 'notahostname removed, got status NXDOMAIN (PROD)', 'result': True, 'secondary': [], 'warnings': []}),
        ("existinghostname", {'message': "existinghostname returned valid answer of '1.2.3.2', not removed (PROD)", 'result': False, 'secondary': [], 'warnings': []}),
        ("newhostname", {'message': 'newhostname removed, got status NXDOMAIN (PROD)', 'result': True, 'secondary': [], 'warnings': []}),
    ])
    def test_dns_verify_remove(self, setup_checks, hostname, result):
        """
        Test checks for verifying a removed record
        """
        foo = setup_checks.verify_removed_name(hostname)
        assert foo == result

    @pytest.mark.parametrize(("hostname", "newval", "result"), [
        ("addedname2", "1.2.3.12", {'message': "change addedname2 from '1.2.3.13' to '1.2.3.12' (TEST)", 'result': True, 'secondary': [], 'warnings': ['no reverse DNS appears to be set for 1.2.3.12 (TEST)']}),
    ])
    def test_dns_change(self, setup_checks, hostname, newval, result):
        """
        Test checks for changing a record in DNS (same name, new value)
        """
        foo = setup_checks.check_changed_name(hostname, newval)
        assert foo == result

    @pytest.mark.parametrize(("hostname", "newval", "result"), [
        ("addedhostname", "1.2.3.3", {'message': "change addedhostname value to '1.2.3.3' (PROD)", 'result': True, 'secondary': [], 'warnings': ['no reverse DNS appears to be set for 1.2.3.3 (PROD)']}),
    ])
    def test_dns_verify_change(self, setup_checks, hostname, newval, result):
        """
        Test checks for verifying a changed record in DNS (same name, new value)
        """
        foo = setup_checks.verify_changed_name(hostname, newval)
        assert foo == result

    @pytest.mark.parametrize(("oldname", "newname", "result"), [
        ("renametest1", "renametest1b", {'message': 'rename renametest1 => renametest1b (TEST)', 'result': True, 'secondary': [], 'warnings': ['no reverse DNS appears to be set for 1.2.3.20 (TEST)']}),
        ("renametest2", "renametest2b", {'message': 'rename renametest2 => renametest2b (TEST)', 'result': True, 'secondary': [], 'warnings': ['renametest2 appears to still have reverse DNS set to renametest2.example.com (TEST)']}),
        ("renametest3", "renametest3b", {'message': 'rename renametest3 => renametest3b (TEST)', 'result': True, 'secondary': ['reverse DNS is set correctly for 1.2.3.22 (TEST)'], 'warnings': []}),
    ])
    def test_dns_rename(self, setup_checks, oldname, newname, result):
        """
        Test checks for renaming a record in DNS (new name, same value)
        """
        foo = setup_checks.check_renamed_name(oldname, newname)
        assert foo == result

    @pytest.mark.parametrize(("oldname", "newname", "result"), [
        ("addedname2", "1.2.3.12", {}),
    ])
    def test_dns_verify_rename(self, setup_checks, oldname, newname, result):
        """
        Test checks for verifying a renamed record in DNS (new name, same value)
        """
        foo = setup_checks.verify_renamed_name(oldname, newname)
        assert foo == result
