"""
tests for dnstest.py main function

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
import shutil
import mock

from pydnstest.checks import DNStestChecks
from pydnstest.config import DnstestConfig
import pydnstest.main
from pydnstest.parser import DnstestParser
from pydnstest.version import VERSION as pydnstest_version

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
    """
    object to mock optparse return object
    """

    def __init__(self):
        """
        preseed with default values
        """
        self.verify = False
        self.config_file = None
        self.testfile = None
        self.ignorettl = False
        self.sleep = None
        self.exampleconf = False
        self.configprint = False
        self.promptconfig = False


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
        config.ignore_ttl = False

        parser = DnstestParser()
        pydnstest.parser = parser

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
        config.ignore_ttl = False

        parser = DnstestParser()
        pydnstest.parser = parser

        chk = DNStestChecks(config)
        # stub
        chk.DNS.resolve_name = self.stub_resolve_name_verify
        # stub
        chk.DNS.lookup_reverse = self.stub_lookup_reverse_verify
        return (parser, chk)

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
        request.addfinalizer(self.remove_testfile)

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
        setattr(opt, "config_file", "dnstest.foo")
        pydnstest.main.sys.stdin = ["foo bar baz"]
        foo = pydnstest.main.main(opt)
        out, err = capfd.readouterr()
        assert foo == None
        assert out == "ERROR: could not parse input line, SKIPPING: foo bar baz\n++++ All 0 tests passed. (pydnstest %s)\n" % pydnstest_version
        assert err == "WARNING: reading from STDIN. Run with '-f filename' to read tests from a file.\n"

    def test_discovered_config_file(self, save_user_config, capfd):
        """
        Test calling main() with a discovered config file
        """
        opt = OptionsObject()

        # write out an example config file
        # this will be cleaned up by restore_user_config()
        fpath = os.path.abspath("dnstest.ini")
        self.write_conf_file(fpath, "[servers]\nprod: 1.2.3.4\ntest: 1.2.3.5\n[defaults]\nhave_reverse_dns: True\ndomain: .example.com\nignore_ttl: False\n")

        pydnstest.main.sys.stdin = ["foo bar baz"]
        foo = None

        foo = pydnstest.main.main(opt)
        out, err = capfd.readouterr()
        assert foo == None
        assert out == "ERROR: could not parse input line, SKIPPING: foo bar baz\n++++ All 0 tests passed. (pydnstest %s)\n" % pydnstest_version
        assert err == "WARNING: reading from STDIN. Run with '-f filename' to read tests from a file.\n"

    def test_no_config_file(self, save_user_config, capfd):
        """
        Test calling main() with a specified config file
        """
        opt = OptionsObject()

        pydnstest.main.sys.stdin = ["foo bar baz"]
        foo = None

        with pytest.raises(SystemExit) as excinfo:
            foo = pydnstest.main.main(opt)
        assert excinfo.value.code == 1
        out, err = capfd.readouterr()
        assert foo == None
        assert out == "ERROR: no configuration file found. Run with --promptconfig to build one interactively, or --example-config for an example.\n"
        assert err == ""

    def test_stdin(self, save_user_config, capfd, monkeypatch):
        """
        Test main() reading from stdin
        """
        opt = OptionsObject()

        pydnstest.main.sys.stdin = ["foo bar baz"]
        foo = None

        def mockreturn(foo, bar, baz):
            return {'result': True, 'message': 'foobarbaz', 'secondary': [], 'warnings': []}
        monkeypatch.setattr(pydnstest.main, "run_check_line", mockreturn)

        # write out an example config file
        # this will be cleaned up by restore_user_config()
        fpath = os.path.abspath("dnstest.ini")
        self.write_conf_file(fpath, "[servers]\nprod: 1.2.3.4\ntest: 1.2.3.5\n[defaults]\nhave_reverse_dns: True\ndomain: .example.com\nignore_ttl: False\n")

        foo = pydnstest.main.main(opt)
        out, err = capfd.readouterr()
        assert foo == None
        assert out == "OK: foobarbaz\n++++ All 1 tests passed. (pydnstest %s)\n" % pydnstest_version
        assert err == "WARNING: reading from STDIN. Run with '-f filename' to read tests from a file.\n"

    def test_testfile_noexist(self, save_user_config, capfd):
        """
        Test with a testfile specified by not existant.
        """
        opt = OptionsObject()
        setattr(opt, "testfile", 'nofilehere')

        # write out an example config file
        # this will be cleaned up by restore_user_config()
        fpath = os.path.abspath("dnstest.ini")
        self.write_conf_file(fpath, "[servers]\nprod: 1.2.3.4\ntest: 1.2.3.5\n[defaults]\nhave_reverse_dns: True\ndomain: .example.com\nignore_ttl: False\n")

        foo = None

        with pytest.raises(SystemExit) as excinfo:
            foo = pydnstest.main.main(opt)
        assert excinfo.value.code == 1
        out, err = capfd.readouterr()
        assert foo == None
        assert out == "ERROR: test file 'nofilehere' does not exist.\n"
        assert err == ""

    def test_check_with_testfile(self, write_testfile, save_user_config, capfd, monkeypatch):
        """
        Test with a testfile.
        """
        def mockreturn(foo, bar, baz):
            return {'result': True, 'message': 'foobarbaz', 'secondary': [], 'warnings': []}
        monkeypatch.setattr(pydnstest.main, "run_check_line", mockreturn)

        opt = OptionsObject()
        setattr(opt, "testfile", 'testfile.txt')

        # write out an example config file
        # this will be cleaned up by restore_user_config()
        fpath = os.path.abspath("dnstest.ini")
        self.write_conf_file(fpath, "[servers]\nprod: 1.2.3.4\ntest: 1.2.3.5\n[defaults]\nhave_reverse_dns: True\ndomain: .example.com\nignore_ttl: False\n")

        foo = pydnstest.main.main(opt)
        out, err = capfd.readouterr()
        assert foo == None
        assert out == "OK: foobarbaz\nOK: foobarbaz\n++++ All 2 tests passed. (pydnstest %s)\n" % pydnstest_version
        assert err == ""

    def test_verify_with_testfile(self, write_testfile, save_user_config, capfd, monkeypatch):
        """
        Test with a testfile.
        """
        def mockreturn(foo, bar, baz):
            if foo == "confirm bar.jasonantman.com":
                return {'result': False, 'message': 'foofail', 'secondary': [], 'warnings': []}
            return {'result': True, 'message': 'foobarbaz', 'secondary': [], 'warnings': []}
        monkeypatch.setattr(pydnstest.main, "run_verify_line", mockreturn)

        opt = OptionsObject()
        setattr(opt, "verify", True)
        setattr(opt, "testfile", 'testfile.txt')

        # write out an example config file
        # this will be cleaned up by restore_user_config()
        fpath = os.path.abspath("dnstest.ini")
        self.write_conf_file(fpath, "[servers]\nprod: 1.2.3.4\ntest: 1.2.3.5\n[defaults]\nhave_reverse_dns: True\ndomain: .example.com\nignore_ttl: False\n")

        foo = pydnstest.main.main(opt)
        out, err = capfd.readouterr()
        assert foo == None
        assert out == "OK: foobarbaz\n**NG: foofail\n++++ 1 passed / 1 FAILED. (pydnstest %s)\n" % pydnstest_version
        assert err == ""

    def test_verify_with_sleep(self, write_testfile, save_user_config, capfd, monkeypatch):
        """
        Test with a testfile.
        """
        def mockreturn(foo, bar, baz):
            if foo == "confirm bar.jasonantman.com":
                return {'result': False, 'message': 'foofail', 'secondary': [], 'warnings': []}
            return {'result': True, 'message': 'foobarbaz', 'secondary': [], 'warnings': []}
        monkeypatch.setattr(pydnstest.main, "run_verify_line", mockreturn)

        opt = OptionsObject()
        setattr(opt, "verify", True)
        setattr(opt, "testfile", 'testfile.txt')
        setattr(opt, "sleep", 0.001)

        # write out an example config file
        # this will be cleaned up by restore_user_config()
        fpath = os.path.abspath("dnstest.ini")
        self.write_conf_file(fpath, "[servers]\nprod: 1.2.3.4\ntest: 1.2.3.5\n[defaults]\nhave_reverse_dns: True\ndomain: .example.com\nignore_ttl: False\n")

        foo = pydnstest.main.main(opt)
        out, err = capfd.readouterr()
        assert foo == None
        assert out == "Note - will sleep 0.001 seconds between lines\nOK: foobarbaz\n**NG: foofail\n++++ 1 passed / 1 FAILED. (pydnstest %s)\n" % pydnstest_version
        assert err == ""

    def test_verify_with_ignorettl(self, write_testfile, save_user_config, capfd, monkeypatch):
        """
        Test with a testfile.
        """
        def mockreturn(foo, bar, baz):
            if foo == "confirm bar.jasonantman.com":
                return {'result': False, 'message': 'foofail', 'secondary': [], 'warnings': []}
            return {'result': True, 'message': 'foobarbaz', 'secondary': [], 'warnings': []}
        monkeypatch.setattr(pydnstest.main, "run_verify_line", mockreturn)

        opt = OptionsObject()
        setattr(opt, "verify", True)
        setattr(opt, "testfile", 'testfile.txt')
        setattr(opt, "ignorettl", True)

        # write out an example config file
        # this will be cleaned up by restore_user_config()
        fpath = os.path.abspath("dnstest.ini")
        self.write_conf_file(fpath, "[servers]\nprod: 1.2.3.4\ntest: 1.2.3.5\n[defaults]\nhave_reverse_dns: True\ndomain: .example.com\nignore_ttl: False\n")

        foo = pydnstest.main.main(opt)
        out, err = capfd.readouterr()
        assert foo == None
        assert out == "OK: foobarbaz\n**NG: foofail\n++++ 1 passed / 1 FAILED. (pydnstest %s)\n" % pydnstest_version
        assert err == ""

    def test_options(self, monkeypatch):
        """
        Test the parse_opts option parsing method
        """
        def mockreturn(options):
            assert options.verify == True
            assert options.config_file == "configfile"
            assert options.testfile == "mytestfile"
            assert options.ignorettl == False
        monkeypatch.setattr(pydnstest.main, "main", mockreturn)
        sys.argv = ['pydnstest', '-c', 'configfile', '-f', 'mytestfile', '-V']
        x = pydnstest.main.parse_opts()

    def test_options_sleep(self, monkeypatch):
        """
        Test the parse_opts option parsing method, with the sleep option
        """
        def mockreturn(options):
            assert options.verify == True
            assert options.config_file == "configfile"
            assert options.testfile == "mytestfile"
            assert options.ignorettl == False
            assert options.sleep == 0.01
        monkeypatch.setattr(pydnstest.main, "main", mockreturn)
        sys.argv = ['pydnstest', '-c', 'configfile', '-f', 'mytestfile', '-V', '--sleep', '0.01']
        x = pydnstest.main.parse_opts()

    def test_options_ignorettl(self, monkeypatch):
        """
        Test the parse_opts option parsing method, with the ignorettl option
        """
        def mockreturn(options):
            assert options.verify == True
            assert options.config_file == "configfile"
            assert options.testfile == "mytestfile"
            assert options.ignorettl == True
        monkeypatch.setattr(pydnstest.main, "main", mockreturn)
        sys.argv = ['pydnstest', '-c', 'configfile', '-f', 'mytestfile', '-V', '--ignore-ttl']
        x = pydnstest.main.parse_opts()

    def test_options_exampleconf(self, monkeypatch):
        """
        Test the parse_opts option parsing method, with the --example-config option sent
        """
        def mockreturn(options):
            assert options.exampleconf == True
        monkeypatch.setattr(pydnstest.main, "main", mockreturn)
        sys.argv = ['pydnstest', '--example-config']
        x = pydnstest.main.parse_opts()

    def test_exampleconf(self, save_user_config, capfd):
        """
        Test calling main() with options.exampleconf == True
        """
        fpath = os.path.abspath("dnstest.ini.example")
        with open(fpath, 'r') as fh:
            expected = fh.read()
        opt = OptionsObject()
        setattr(opt, "exampleconf", True)
        pydnstest.main.sys.stdin = ["foo bar baz"]
        with pytest.raises(SystemExit):
            pydnstest.main.main(opt)
        out, err = capfd.readouterr()
        assert out.strip() == expected.strip()
        assert err == ""

    def test_options_configprint(self, monkeypatch):
        """
        Test the parse_opts option parsing method, with the --configprint option sent
        """
        def mockreturn(options):
            assert options.configprint == True
        monkeypatch.setattr(pydnstest.main, "main", mockreturn)
        sys.argv = ['pydnstest', '--configprint']
        x = pydnstest.main.parse_opts()

    def test_configprint(self, save_user_config, capfd):
        """
        Test calling main() with options.configprint == True
        """
        fpath = os.path.abspath("dnstest.ini.example")
        with open(fpath, 'r') as fh:
            expected = fh.read()
        expected = "# {fpath}\n".format(fpath=fpath) + expected
        opt = OptionsObject()
        setattr(opt, "configprint", True)
        setattr(opt, "config_file", fpath)
        pydnstest.main.sys.stdin = ["foo bar baz"]
        with pytest.raises(SystemExit):
            pydnstest.main.main(opt)
        out, err = capfd.readouterr()
        assert out.strip() == expected.strip()
        assert err == ""

    def test_options_promptconfig(self, monkeypatch):
        """
        Test the parse_opts option parsing method, with the --promptconfig option sent
        """
        def mockreturn(options):
            assert options.promptconfig == True
        monkeypatch.setattr(pydnstest.main, "main", mockreturn)
        sys.argv = ['pydnstest', '--promptconfig']
        x = pydnstest.main.parse_opts()

    def test_promptconfig(self, save_user_config, capfd):
        """
        Test calling main() with options.promptconfig == True
        """
        opt = OptionsObject()
        setattr(opt, "promptconfig", True)
        prompt_config_mock = mock.MagicMock()
        find_config_mock = mock.MagicMock()
        find_config_mock.return_value = '/foo/bar/dnstest.ini'

        with mock.patch('pydnstest.main.DnstestConfig.prompt_config', prompt_config_mock):
            with mock.patch('pydnstest.main.DnstestConfig.find_config_file', find_config_mock):
                with pytest.raises(SystemExit):
                    pydnstest.main.main(opt)
        assert prompt_config_mock.call_count == 1

    def test_options_help(self, save_user_config, capfd):
        """
        test --help output
        """
        grammar_mock = mock.MagicMock()
        grammar_mock.return_value = ["outputhere"]
        with mock.patch('pydnstest.main.DnstestParser.get_grammar', grammar_mock):
            with mock.patch('pydnstest.main.sys.argv', ['pydnstest', '--help']):
                with pytest.raises(SystemExit):
                    pydnstest.main.parse_opts()
        out, err = capfd.readouterr()
        assert "Grammar:\n\noutputhere\n" in out
        assert err == ""
