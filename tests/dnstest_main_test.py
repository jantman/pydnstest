# tests for dnstest.py main function

import pytest
import sys
import os
import shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../')

from dnstest_checks import DNStestChecks
from dnstest_config import DnstestConfig
import dnstest
from dnstest_parser import DnstestParser

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

known_dns['ver']['prod']['fwd']['testrvl5.example.com'] = ['1.2.1.5', 'A']
known_dns['ver']['test']['fwd']['testrvl5.example.com'] = ['1.2.1.5', 'A']


class OptionsObject(object):
    pass


class TestDNSTestMain:
    """
    Tests the dnstest.py script main function
    """

    ########################################
    # overall setup and mocked DNS queries #
    ########################################

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

        parser = DnstestParser()
        dnstest.parser = parser

        chk = DNStestChecks(config)
        # stub
        chk.DNS.resolve_name = self.stub_resolve_name
        # stub
        chk.DNS.lookup_reverse = self.stub_lookup_reverse
        return (parser, chk)

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

        parser = DnstestParser()
        dnstest.parser = parser

        chk = DNStestChecks(config)
        # stub
        chk.DNS.resolve_name = self.stub_resolve_name_verify
        # stub
        chk.DNS.lookup_reverse = self.stub_lookup_reverse_verify
        return (parser, chk)

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

    ###############################
    # mocked config file handling #
    ###############################

    @pytest.fixture
    def save_user_config(self, request):
        """
        Rename any existing configuration files prior to testing
        """
        if os.path.exists("dnstest.ini"):
            shutil.move(os.path.abspath("dnstest.ini"), os.path.abspath("dnstest.ini.pretest"))
        if os.path.exists(os.path.expanduser("~/.dnstest.ini")):
            shutil.move(os.path.expanduser("~/.dnstest.ini"), os.path.expanduser("~/.dnstest.ini.pretest"))
        request.addfinalizer(self.restore_user_config)

    def restore_user_config(self):
        """
        Remove any config files generated by testing, and restore previous configs
        """
        # teardown
        if os.path.exists("dnstest.ini"):
            os.remove("dnstest.ini")
        if os.path.exists(os.path.expanduser("~/.dnstest.ini")):
            os.remove(os.path.expanduser("~/.dnstest.ini"))

        if os.path.exists("dnstest.ini.pretest"):
            shutil.move(os.path.abspath("dnstest.ini.pretest"), os.path.abspath("dnstest.ini"))
        if os.path.exists(os.path.expanduser("~/.dnstest.ini.pretest")):
            shutil.move(os.path.expanduser("~/.dnstest.ini.pretest"), os.path.expanduser("~/.dnstest.ini"))
        return True

    def write_conf_file(self, path, contents):
        fh = open(path, 'w')
        fh.write(contents)
        fh.close()
        return

    @pytest.fixture
    def write_testfile(self, request):
        """
        Write a sample testfile
        """
        fname = "testfile.txt"
        fh = open(fname, 'w')
        fh.write("confirm foo.jasonantman.com\n\n#foo\nconfirm bar.jasonantman.com\n")
        fh.close()
        request.addfinalizer(self.restore_user_config)

    def remove_testfile(self):
        """
        Remove the testfile
        """
        # teardown
        os.remove("testfile.txt")
        return True

    ###########################################
    # Done with setup, start the actual tests #
    ###########################################

    def test_specified_config_file(self, save_user_config, capfd):
        """
        Test calling main() with a specified config file
        """
        opt = OptionsObject()
        setattr(opt, "verify", False)
        setattr(opt, "config_file", "dnstest.foo")
        setattr(opt, "testfile", False)
        #opt.config_file = "dnstest.foo"
        dnstest.sys.stdin = ["foo bar baz"]
        foo = dnstest.main(opt)
        out, err = capfd.readouterr()
        assert foo == None
        assert out == "ERROR: could not parse input line, SKIPPING: foo bar baz\n++++ All 0 tests passed.\n"
        assert err == ""

    def test_discovered_config_file(self, save_user_config, capfd):
        """
        Test calling main() with a discovered config file
        """
        opt = OptionsObject()
        setattr(opt, "verify", False)
        setattr(opt, "config_file", False)
        setattr(opt, "testfile", False)

        # write out an example config file
        # this will be cleaned up by restore_user_config()
        fpath = os.path.abspath("dnstest.ini")
        self.write_conf_file(fpath, "[servers]\nprod: 1.2.3.4\ntest: 1.2.3.5\n[defaults]\nhave_reverse_dns: True\ndomain: .example.com\n")

        dnstest.sys.stdin = ["foo bar baz"]
        foo = None

        foo = dnstest.main(opt)
        out, err = capfd.readouterr()
        assert foo == None
        assert out == "ERROR: could not parse input line, SKIPPING: foo bar baz\n++++ All 0 tests passed.\n"
        assert err == ""

    def test_no_config_file(self, save_user_config, capfd):
        """
        Test calling main() with a specified config file
        """
        opt = OptionsObject()
        setattr(opt, "verify", False)
        setattr(opt, "config_file", False)
        setattr(opt, "testfile", False)

        dnstest.sys.stdin = ["foo bar baz"]
        foo = None

        with pytest.raises(SystemExit) as excinfo:
            foo = dnstest.main(opt)
        assert excinfo.value.code == 1
        out, err = capfd.readouterr()
        assert foo == None
        assert out == "ERROR: no configuration file.\n"
        assert err == ""

    def test_testfile_noexist(self, save_user_config, capfd):
        """
        Test with a testfile specified by not existant.
        """
        opt = OptionsObject()
        setattr(opt, "verify", False)
        setattr(opt, "config_file", False)
        setattr(opt, "testfile", 'nofilehere')

        # write out an example config file
        # this will be cleaned up by restore_user_config()
        fpath = os.path.abspath("dnstest.ini")
        self.write_conf_file(fpath, "[servers]\nprod: 1.2.3.4\ntest: 1.2.3.5\n[defaults]\nhave_reverse_dns: True\ndomain: .example.com\n")

        foo = None

        with pytest.raises(SystemExit) as excinfo:
            foo = dnstest.main(opt)
        assert excinfo.value.code == 1
        out, err = capfd.readouterr()
        assert foo == None
        assert out == "ERROR: test file 'nofilehere' does not exist.\n"
        assert err == ""

    def test_check_with_testfile(self, write_testfile, capfd, monkeypatch):
        """
        Test with a testfile.
        """
        def mockreturn(foo, bar, baz):
            return {'result': True, 'message': 'foobarbaz', 'secondary': [], 'warnings': []}
        monkeypatch.setattr(dnstest, "run_check_line", mockreturn)

        opt = OptionsObject()
        setattr(opt, "verify", False)
        setattr(opt, "config_file", False)
        setattr(opt, "testfile", 'testfile.txt')

        # write out an example config file
        # this will be cleaned up by restore_user_config()
        fpath = os.path.abspath("dnstest.ini")
        self.write_conf_file(fpath, "[servers]\nprod: 1.2.3.4\ntest: 1.2.3.5\n[defaults]\nhave_reverse_dns: True\ndomain: .example.com\n")

        foo = dnstest.main(opt)
        out, err = capfd.readouterr()
        assert foo == None
        assert out == "OK: foobarbaz\nOK: foobarbaz\n++++ All 2 tests passed.\n"
        assert err == ""

    def test_verify_with_testfile(self, write_testfile, capfd, monkeypatch):
        """
        Test with a testfile.
        """
        def mockreturn(foo, bar, baz):
            if foo == "confirm bar.jasonantman.com":
                return {'result': False, 'message': 'foofail', 'secondary': [], 'warnings': []}
            return {'result': True, 'message': 'foobarbaz', 'secondary': [], 'warnings': []}
        monkeypatch.setattr(dnstest, "run_verify_line", mockreturn)

        opt = OptionsObject()
        setattr(opt, "verify", True)
        setattr(opt, "config_file", False)
        setattr(opt, "testfile", 'testfile.txt')

        # write out an example config file
        # this will be cleaned up by restore_user_config()
        fpath = os.path.abspath("dnstest.ini")
        self.write_conf_file(fpath, "[servers]\nprod: 1.2.3.4\ntest: 1.2.3.5\n[defaults]\nhave_reverse_dns: True\ndomain: .example.com\n")

        foo = dnstest.main(opt)
        out, err = capfd.readouterr()
        assert foo == None
        assert out == "OK: foobarbaz\n**NG: foofail\n++++ 1 passed / 1 FAILED.\n"
        assert err == ""
