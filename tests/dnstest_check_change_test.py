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
known_rev_dns['prod_server_stub']['1.2.3.25'] = 'renametest5.example.com'
known_rev_dns['prod_server_stub']['1.2.3.26'] = 'renametest6.example.com'
known_rev_dns['prod_server_stub']['1.9.9.9'] = 'SERVFAIL'

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
known_rev_dns['test_server_stub']['1.2.3.25'] = 'renametest5.example.com'
known_rev_dns['test_server_stub']['1.2.3.26'] = 'renametest6b.example.com'

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
known_dns['prod_server_stub']['renamedname.example.com'] = ['1.2.3.12', 'A']
known_dns['prod_server_stub']['addedname2.example.com'] = ['1.2.3.13', 'A']
known_dns['prod_server_stub']['addedname3.example.com'] = ['1.2.3.14', 'A']
known_dns['prod_server_stub']['addedwithrev.example.com'] = ['1.2.3.16', 'A']
known_dns['prod_server_stub']['addedbadprodrev.example.com'] = ['1.2.3.17', 'A']
known_dns['prod_server_stub']['addedprodrevservfail.example.com'] = ['1.9.9.9', 'A']
known_dns['prod_server_stub']['renametest1.example.com'] = ['1.2.3.20', 'A']
known_dns['prod_server_stub']['renametest2.example.com'] = ['1.2.3.21', 'A']
known_dns['prod_server_stub']['renametest3.example.com'] = ['1.2.3.22', 'A']
known_dns['prod_server_stub']['renametest4.example.com'] = ['1.2.3.23', 'A']
known_dns['prod_server_stub']['renametest5.example.com'] = ['1.2.3.25', 'A']
known_dns['prod_server_stub']['renametest6b.example.com'] = ['1.2.3.26', 'A']
known_dns['prod_server_stub']['servfail-prod'] = ['STATUS', 'SERVFAIL']
known_dns['prod_server_stub']['servfail-prod.example.com'] = ['STATUS', 'SERVFAIL']
known_dns['prod_server_stub']['servall-test'] = ['STATUS', 'SERVFAIL']
known_dns['prod_server_stub']['servfail-all.example.com'] = ['STATUS', 'SERVFAIL']

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
known_dns['test_server_stub']['renametest4b.example.com'] = ['1.2.3.23', 'A']
known_dns['test_server_stub']['renametest5b.example.com'] = ['1.2.3.25', 'A']
known_dns['test_server_stub']['renametest6b.example.com'] = ['1.2.3.26', 'A']
known_dns['test_server_stub']['servfail-test'] = ['STATUS', 'SERVFAIL']
known_dns['test_server_stub']['servfail-test.example.com'] = ['STATUS', 'SERVFAIL']
known_dns['test_server_stub']['servfail-test2'] = ['STATUS', 'SERVFAIL']
known_dns['test_server_stub']['servfail-test2.example.com'] = ['STATUS', 'SERVFAIL']
known_dns['test_server_stub']['servall-test'] = ['STATUS', 'SERVFAIL']
known_dns['test_server_stub']['servfail-all.example.com'] = ['STATUS', 'SERVFAIL']
known_dns['test_server_stub']['removetest1.example.com'] = ['1.2.3.27', 'A']

class TestDNSCheckChange:
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

        if query in known_dns[to_server] and known_dns[to_server][query][0] == "STATUS":
            return {'status': known_dns[to_server][query][1]}
        elif query in known_dns[to_server]:
            return {'answer': {'name': query, 'data': known_dns[to_server][query][0], 'typename': known_dns[to_server][query][1], 'classstr': 'IN', 'ttl': 360, 'type': 5, 'class': 1, 'rdlength': 14}}
        else:
            return {'status': 'NXDOMAIN'}

    def stub_lookup_reverse(self, name, to_server, to_port=53):
        """
        stub method

        return a dict that looks like the return value from dnstest.lookup_reverse
        but either returns one of a hard-coded group of dicts, or an error.
        """

        if name in known_rev_dns[to_server] and known_rev_dns[to_server][name] == "SERVFAIL":
            return {'status': 'SERVFAIL'}
        elif name in known_rev_dns[to_server]:
            return {'answer': {'name': name, 'data': known_rev_dns[to_server][name], 'typename': 'PTR', 'classstr': 'IN', 'ttl': 360, 'type': 12, 'class': 1, 'rdlength': 33}}
        else:
            return {'status': 'NXDOMAIN'}

    ###########################################
    # Done with setup, start the actual tests #
    ###########################################

    @pytest.mark.parametrize(("hostname", "newval", "result"), [
        ("addedname2", "1.2.3.12", {'message': "change addedname2 from '1.2.3.13' to '1.2.3.12' (TEST)", 'result': True, 'secondary': [], 'warnings': ['REVERSE NG: no reverse DNS appears to be set for 1.2.3.12 (TEST)']}),
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
