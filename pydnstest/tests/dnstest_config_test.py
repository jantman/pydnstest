"""
tests for dnstest_config.py

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
import os.path
import os
import mock

# conditional imports for packages with different names in python 2 and 3
if sys.version_info[0] == 3:
    import configparser as ConfigParser
    from configparser import ParsingError
else:
    import ConfigParser
    from ConfigParser import ParsingError

from pydnstest.config import DnstestConfig


class TestConfigMethods:
    """
    Class to test the configuration-related methods in dnstest_config
    """

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

    def test_find_no_config_file(self, save_user_config):
        dc = DnstestConfig()
        assert dc.find_config_file() == None

    def write_conf_file(self, path, contents):
        fh = open(path, 'w')
        fh.write(contents)
        fh.close()
        return

    def test_find_main_config_file(self, save_user_config):
        dc = DnstestConfig()
        fpath = os.path.abspath("dnstest.ini")
        self.write_conf_file(fpath, "test_find_main_config_file")
        assert dc.find_config_file() == fpath

    def test_find_dot_config_file(self, save_user_config):
        dc = DnstestConfig()
        fpath = os.path.expanduser("~/.dnstest.ini")
        self.write_conf_file(fpath, "test_find_dot_config_file")
        assert dc.find_config_file() == fpath

    def test_parse_example_config_file(self, save_user_config):
        dc = DnstestConfig()
        fpath = os.path.abspath("dnstest.ini.example")
        dc.load_config(fpath)
        assert dc.server_prod == '1.2.3.4'
        assert dc.server_test == '1.2.3.5'
        assert dc.default_domain == '.example.com'
        assert dc.have_reverse_dns == True
        assert dc.ignore_ttl == False
        assert dc.sleep == 0.0
        assert dc.asDict() == {'default_domain': '.example.com', 'have_reverse_dns': True,
                               'servers': {'prod': '1.2.3.4', 'test': '1.2.3.5'}, 'ignore_ttl': False, 'sleep': 0.0}

    def test_parse_bad_config_file(self, save_user_config):
        fpath = os.path.abspath("dnstest.ini")
        contents = """
[servers]
blarg

"""
        self.write_conf_file(fpath, contents)
        dc = DnstestConfig()
        with pytest.raises(ParsingError):
            dc.load_config(fpath)

    def test_parse_empty_config_file(self, save_user_config):
        dc = DnstestConfig()
        fpath = os.path.abspath("dnstest.ini")
        contents = ""
        self.write_conf_file(fpath, contents)
        dc.load_config(fpath)
        assert dc.server_prod == ''
        assert dc.server_test == ''
        assert dc.default_domain == ''
        assert dc.have_reverse_dns == True
        assert dc.ignore_ttl == False
        assert dc.sleep == 0.0

    def test_example_config_to_string(self):
        """ test converting the example config to a string """
        fpath = os.path.abspath("dnstest.ini.example")
        with open(fpath, 'r') as fh:
            expected = fh.read()
        dc = DnstestConfig()
        dc.server_prod = '1.2.3.4'
        dc.server_test = '1.2.3.5'
        dc.default_domain = '.example.com'
        dc.have_reverse_dns = True
        dc.ignore_ttl = False
        dc.sleep = 0.0
        result = dc.to_string()
        assert result == expected

    def test_set_example_values(self):
        """ test converting the example config to a string """
        dc = DnstestConfig()
        dc.set_example_values()
        assert dc.server_prod == '1.2.3.4'
        assert dc.server_test == '1.2.3.5'
        assert dc.default_domain == '.example.com'
        assert dc.have_reverse_dns == True
        assert dc.ignore_ttl == False
        assert dc.sleep == 0.0

    def test_confirm_response_yes(self):
        dc = DnstestConfig()
        input_mock = mock.MagicMock()
        input_mock.return_value = 'yes'
        with mock.patch('pydnstest.config.DnstestConfig.input_wrapper', input_mock):
            foo = dc.confirm_response('foo')
        assert input_mock.call_count == 1
        assert input_mock.call_args == mock.call("Is 'foo' correct? [y/N] ")
        assert foo == True

    def test_confirm_response_no(self):
        dc = DnstestConfig()
        input_mock = mock.MagicMock()
        input_mock.return_value = "no\n"
        with mock.patch('pydnstest.config.DnstestConfig.input_wrapper', input_mock):
            foo = dc.confirm_response('foo')
        assert input_mock.call_count == 1
        assert input_mock.call_args == mock.call("Is 'foo' correct? [y/N] ")
        assert foo == False

    def test_confirm_response_empty(self):
        dc = DnstestConfig()
        input_mock = mock.MagicMock()
        input_mock.return_value = "\n"
        with mock.patch('pydnstest.config.DnstestConfig.input_wrapper', input_mock):
            foo = dc.confirm_response('foo')
        assert input_mock.call_count == 1
        assert input_mock.call_args == mock.call("Is 'foo' correct? [y/N] ")
        assert foo == False

    def test_prompt_input(self):
        input_mock = mock.MagicMock()
        input_mock.return_value = '1.2.3.4'
        confirm_mock = mock.MagicMock()
        confirm_mock.return_value = True

        dc = DnstestConfig()
        with mock.patch('pydnstest.config.DnstestConfig.input_wrapper', input_mock):
            with mock.patch('pydnstest.config.DnstestConfig.confirm_response', confirm_mock):
                foo = dc.prompt_input("foo")
        assert input_mock.call_count == 1
        assert input_mock.call_args == mock.call("foo: ")
        assert confirm_mock.call_count == 1
        assert foo == '1.2.3.4'

    def test_prompt_input_default(self):
        input_mock = mock.MagicMock()
        input_mock.return_value = ''
        confirm_mock = mock.MagicMock()
        confirm_mock.return_value = True

        dc = DnstestConfig()
        with mock.patch('pydnstest.config.DnstestConfig.input_wrapper', input_mock):
            with mock.patch('pydnstest.config.DnstestConfig.confirm_response', confirm_mock):
                foo = dc.prompt_input("foo", default='bar')
        assert input_mock.call_count == 1
        assert input_mock.call_args == mock.call("foo (default: bar): ")
        assert confirm_mock.call_count == 1
        assert foo == 'bar'

    def test_prompt_input_default_true(self):
        input_mock = mock.MagicMock()
        input_mock.return_value = ''
        confirm_mock = mock.MagicMock()
        confirm_mock.return_value = True
        validate_mock = mock.MagicMock()
        validate_mock.return_value = True

        dc = DnstestConfig()
        with mock.patch('pydnstest.config.DnstestConfig.input_wrapper', input_mock):
            with mock.patch('pydnstest.config.DnstestConfig.confirm_response', confirm_mock):
                foo = dc.prompt_input("foo", default=True, validate_cb=validate_mock)
        assert input_mock.call_count == 1
        assert input_mock.call_args == mock.call("foo (default: y): ")
        assert validate_mock.call_count == 1
        assert validate_mock.call_args == mock.call('y')
        assert confirm_mock.call_count == 1
        assert confirm_mock.call_args == mock.call('y')
        assert foo == True

    def test_prompt_input_default_false(self):
        input_mock = mock.MagicMock()
        input_mock.return_value = ''
        confirm_mock = mock.MagicMock()
        confirm_mock.return_value = True
        validate_mock = mock.MagicMock()
        validate_mock.return_value = False

        dc = DnstestConfig()
        with mock.patch('pydnstest.config.DnstestConfig.input_wrapper', input_mock):
            with mock.patch('pydnstest.config.DnstestConfig.confirm_response', confirm_mock):
                foo = dc.prompt_input("foo", default=False, validate_cb=validate_mock)
        assert input_mock.call_count == 1
        assert input_mock.call_args == mock.call("foo (default: n): ")
        assert validate_mock.call_count == 1
        assert validate_mock.call_args == mock.call('n')
        assert confirm_mock.call_count == 1
        assert confirm_mock.call_args == mock.call('n')
        assert foo == False

    def test_prompt_input_default_false_validate(self):
        input_mock = mock.MagicMock()
        input_mock.return_value = ''
        confirm_mock = mock.MagicMock()
        confirm_mock.return_value = True
        validate_mock = mock.MagicMock()
        validate_mock.return_value = False

        dc = DnstestConfig()
        with mock.patch('pydnstest.config.DnstestConfig.input_wrapper', input_mock):
            with mock.patch('pydnstest.config.DnstestConfig.confirm_response', confirm_mock):
                foo = dc.prompt_input("foo", default=False, validate_cb=validate_mock)
        assert input_mock.call_count == 1
        assert input_mock.call_args == mock.call("foo (default: n): ")
        assert confirm_mock.call_count == 1
        assert validate_mock.call_count == 1
        assert validate_mock.call_args == mock.call('n')
        assert foo == False

    def test_prompt_input_default_float(self):
        input_mock = mock.MagicMock()
        input_mock.return_value = ''
        confirm_mock = mock.MagicMock()
        confirm_mock.return_value = True
        validate_mock = mock.MagicMock()
        validate_mock.return_value = 123.456

        dc = DnstestConfig()
        with mock.patch('pydnstest.config.DnstestConfig.input_wrapper', input_mock):
            with mock.patch('pydnstest.config.DnstestConfig.confirm_response', confirm_mock):
                foo = dc.prompt_input("foo", default=123.456, validate_cb=validate_mock)
        assert input_mock.call_count == 1
        assert input_mock.call_args == mock.call("foo (default: 123.456): ")
        assert confirm_mock.call_count == 1
        assert validate_mock.call_count == 1
        assert validate_mock.call_args == mock.call('123.456')
        assert foo == 123.456

    def test_prompt_input_validate_success(self):
        input_mock = mock.MagicMock()
        input_mock.return_value = 'hello'
        confirm_mock = mock.MagicMock()
        confirm_mock.return_value = True
        validate_mock = mock.MagicMock()
        validate_mock.return_value = 'goodbye'

        dc = DnstestConfig()
        with mock.patch('pydnstest.config.DnstestConfig.input_wrapper', input_mock):
            with mock.patch('pydnstest.config.DnstestConfig.confirm_response', confirm_mock):
                foo = dc.prompt_input("foo", validate_cb=validate_mock)
        assert input_mock.call_count == 1
        assert confirm_mock.call_count == 1
        assert validate_mock.call_count == 1
        assert foo == 'goodbye'

    def test_prompt_input_validate_failure(self, capfd):
        # this is a bit complex, because our mocks need to do different things on first and second calls
        input_returns = ['hello', 'goodbye']

        def input_se(*args):
            return input_returns.pop(0)

        input_mock = mock.MagicMock(side_effect=input_se)
        confirm_mock = mock.MagicMock()
        confirm_mock.return_value = True
        validate_returns = [None, 'eybdoog']

        def validate_se(*args):
            return validate_returns.pop(0)

        validate_mock = mock.MagicMock(side_effect=validate_se)

        dc = DnstestConfig()
        with mock.patch('pydnstest.config.DnstestConfig.input_wrapper', input_mock):
            with mock.patch('pydnstest.config.DnstestConfig.confirm_response', confirm_mock):
                foo = dc.prompt_input("foo", validate_cb=validate_mock)
        assert input_mock.call_count == 2
        out, err = capfd.readouterr()
        assert out == "ERROR: invalid response: hello\n"
        assert err == ""
        assert confirm_mock.call_count == 1
        assert validate_mock.call_count == 2
        assert foo == 'eybdoog'

    def test_prompt_input_no_confirm(self):
        input_mock = mock.MagicMock()
        input_mock.return_value = 'hello'

        def confirm_se(*args):
            return confirm_returns.pop(0)

        confirm_returns = [False, True]
        confirm_mock = mock.MagicMock(side_effect=confirm_se)

        dc = DnstestConfig()
        with mock.patch('pydnstest.config.DnstestConfig.input_wrapper', input_mock):
            with mock.patch('pydnstest.config.DnstestConfig.confirm_response', confirm_mock):
                foo = dc.prompt_input("foo")
        assert input_mock.call_count == 2
        assert confirm_mock.call_count == 2
        assert foo == 'hello'

    @pytest.mark.parametrize(("input_str", "result"), [
        ('1.2.3.4', '1.2.3.4'),
        ('foo', None),
        ('999.999.0.1234', None),
        ('255.1.10.199', '255.1.10.199'),
    ])
    def test_validate_ipaddr(self, input_str, result):
        dc = DnstestConfig()
        assert dc.validate_ipaddr(input_str) == result

    @pytest.mark.parametrize(("input_str", "result"), [
        ('y', True),
        ('Y', True),
        ('yes', True),
        ('t', True),
        ('true', True),
        ('True', True),
        ('on', True),
        ('1', True),
        ('n', False),
        ('no', False),
        ('No', False),
        ('N', False),
        ('f', False),
        ('false', False),
        ('False', False),
        ('0', False),
        ('off', False),
        ('2', None),
        ('foo', None),
    ])
    def test_validate_bool(self, input_str, result):
        dc = DnstestConfig()
        assert dc.validate_bool(input_str) == result

    @pytest.mark.parametrize(("input_str", "result"), [
        ('hello', None),
        ('he1.1o', None),
        ('foo 11.0', None),
        ('11.0 foo', None),
        ('1.234', 1.234),
        ('123', 123),
    ])
    def test_validate_float(self, input_str, result):
        dc = DnstestConfig()
        assert dc.validate_float(input_str) == result

    def test_promptconfig(self, capfd):
        dc = DnstestConfig()
        dc.conf_file = '/foo/bar/baz'

        def prompt_input_se(prompt, default=None, validate_cb=None):
            ret = {
                "Production DNS Server IP": '1.2.3.4',
                "Test/Staging DNS Server IP": '5.6.7.8',
                "Check for reverse DNS by default? [Y|n]": True,
                "Default domain for hostnames (blank for none)": 'example.com',
                "Ignore difference in TTL? [y|N]": False,
                "Sleep between queries (s)": 0.0,
            }
            return ret[prompt]
        prompt_input_mock = mock.MagicMock(side_effect=prompt_input_se)

        confirm_response_mock = mock.MagicMock()
        confirm_response_mock.return_value = True

        to_string_mock = mock.MagicMock()
        to_string_mock.return_value = 'foo bar baz'

        write_mock = mock.MagicMock()
        write_mock.return_value = True

        with mock.patch('pydnstest.config.DnstestConfig.prompt_input', prompt_input_mock):
            with mock.patch('pydnstest.config.DnstestConfig.to_string', to_string_mock):
                with mock.patch('pydnstest.config.DnstestConfig.confirm_response', confirm_response_mock):
                    with mock.patch('pydnstest.config.DnstestConfig.write', write_mock):
                        dc.prompt_config()
        assert prompt_input_mock.call_count == 6
        assert prompt_input_mock.call_args_list == [
            mock.call("Production DNS Server IP", validate_cb=dc.validate_ipaddr),
            mock.call("Test/Staging DNS Server IP", validate_cb=dc.validate_ipaddr),
            mock.call("Check for reverse DNS by default? [Y|n]", default=True, validate_cb=dc.validate_bool),
            mock.call("Default domain for hostnames (blank for none)", default=''),
            mock.call("Ignore difference in TTL? [y|N]", default=False, validate_cb=dc.validate_bool),
            mock.call("Sleep between queries (s)", default=0.0, validate_cb=dc.validate_float),
        ]
        assert to_string_mock.call_count == 1
        assert confirm_response_mock.call_count == 1
        assert confirm_response_mock.call_args == mock.call("Is this configuration correct?")
        assert write_mock.call_count == 1
        out, err = capfd.readouterr()
        assert out == "Configuration:\n#####################\nfoo bar baz\n#####################\n\nConfiguration written to: /foo/bar/baz\n"
        assert err == ""
        assert dc.server_prod == '1.2.3.4'
        assert dc.server_test == '5.6.7.8'
        assert dc.have_reverse_dns == True
        assert dc.default_domain == 'example.com'
        assert dc.ignore_ttl == False
        assert dc.sleep == 0.0

    def test_promptconfig_empty_default_domain(self, capfd):
        dc = DnstestConfig()
        dc.conf_file = '/foo/bar/baz'

        def prompt_input_se(prompt, default=None, validate_cb=None):
            ret = {
                "Production DNS Server IP": '1.2.3.4',
                "Test/Staging DNS Server IP": '5.6.7.8',
                "Check for reverse DNS by default? [Y|n]": True,
                "Default domain for hostnames (blank for none)": '',
                "Ignore difference in TTL? [y|N]": False,
                "Sleep between queries (s)": 0.0,
            }
            return ret[prompt]
        prompt_input_mock = mock.MagicMock(side_effect=prompt_input_se)

        confirm_response_mock = mock.MagicMock()
        confirm_response_mock.return_value = True

        to_string_mock = mock.MagicMock()
        to_string_mock.return_value = 'foo bar baz'

        write_mock = mock.MagicMock()
        write_mock.return_value = True

        with mock.patch('pydnstest.config.DnstestConfig.prompt_input', prompt_input_mock):
            with mock.patch('pydnstest.config.DnstestConfig.to_string', to_string_mock):
                with mock.patch('pydnstest.config.DnstestConfig.confirm_response', confirm_response_mock):
                    with mock.patch('pydnstest.config.DnstestConfig.write', write_mock):
                        dc.prompt_config()
        assert prompt_input_mock.call_count == 6
        assert prompt_input_mock.call_args_list == [
            mock.call("Production DNS Server IP", validate_cb=dc.validate_ipaddr),
            mock.call("Test/Staging DNS Server IP", validate_cb=dc.validate_ipaddr),
            mock.call("Check for reverse DNS by default? [Y|n]", default=True, validate_cb=dc.validate_bool),
            mock.call("Default domain for hostnames (blank for none)", default=''),
            mock.call("Ignore difference in TTL? [y|N]", default=False, validate_cb=dc.validate_bool),
            mock.call("Sleep between queries (s)", default=0.0, validate_cb=dc.validate_float),
        ]
        assert to_string_mock.call_count == 1
        assert confirm_response_mock.call_count == 1
        assert write_mock.call_count == 1
        out, err = capfd.readouterr()
        assert out == "Configuration:\n#####################\nfoo bar baz\n#####################\n\nConfiguration written to: /foo/bar/baz\n"
        assert err == ""
        assert dc.server_prod == '1.2.3.4'
        assert dc.server_test == '5.6.7.8'
        assert dc.have_reverse_dns == True
        assert dc.default_domain == ''
        assert dc.ignore_ttl == False
        assert dc.sleep == 0.0

    def test_promptconfig_no_confirm(self, capfd):
        dc = DnstestConfig()
        dc.conf_file = '/foo/bar/baz'

        def prompt_input_se(prompt, default=None, validate_cb=None):
            ret = {
                "Production DNS Server IP": '1.2.3.4',
                "Test/Staging DNS Server IP": '5.6.7.8',
                "Check for reverse DNS by default? [Y|n]": True,
                "Default domain for hostnames (blank for none)": 'example.com',
                "Ignore difference in TTL? [y|N]": False,
                "Sleep between queries (s)": 0.0,
            }
            return ret[prompt]
        prompt_input_mock = mock.MagicMock(side_effect=prompt_input_se)

        confirm_response_mock = mock.MagicMock()
        confirm_response_mock.return_value = False

        to_string_mock = mock.MagicMock()
        to_string_mock.return_value = 'foo bar baz'

        write_mock = mock.MagicMock()
        write_mock.return_value = True

        with mock.patch('pydnstest.config.DnstestConfig.prompt_input', prompt_input_mock):
            with mock.patch('pydnstest.config.DnstestConfig.to_string', to_string_mock):
                with mock.patch('pydnstest.config.DnstestConfig.confirm_response', confirm_response_mock):
                    with mock.patch('pydnstest.config.DnstestConfig.write', write_mock):
                        with pytest.raises(SystemExit) as excinfo:
                            dc.prompt_config()
        assert excinfo.value.code == "Exiting on user request. No configuration written."
        assert prompt_input_mock.call_count == 6
        assert prompt_input_mock.call_args_list == [
            mock.call("Production DNS Server IP", validate_cb=dc.validate_ipaddr),
            mock.call("Test/Staging DNS Server IP", validate_cb=dc.validate_ipaddr),
            mock.call("Check for reverse DNS by default? [Y|n]", default=True, validate_cb=dc.validate_bool),
            mock.call("Default domain for hostnames (blank for none)", default=''),
            mock.call("Ignore difference in TTL? [y|N]", default=False, validate_cb=dc.validate_bool),
            mock.call("Sleep between queries (s)", default=0.0, validate_cb=dc.validate_float),
        ]
        assert to_string_mock.call_count == 1
        assert confirm_response_mock.call_count == 1
        assert write_mock.call_count == 0
        out, err = capfd.readouterr()
        assert out == "Configuration:\n#####################\nfoo bar baz\n#####################\n\n"
        assert err == ""
        assert dc.server_prod == '1.2.3.4'
        assert dc.server_test == '5.6.7.8'
        assert dc.have_reverse_dns == True
        assert dc.default_domain == 'example.com'
        assert dc.ignore_ttl == False
        assert dc.sleep == 0.0

    def test_write(self, save_user_config):
        """ test writing the file to disk """
        dc = DnstestConfig()
        conf_str = dc.to_string()
        mock_open = mock.mock_open()
        if sys.version_info[0] == 3:
            mock_target = 'builtins.open'
        else:
            mock_target = '__builtin__.open'

        with mock.patch(mock_target, mock_open, create=True):
            dc.write()
        assert mock_open.call_count == 1
        fh = mock_open.return_value.__enter__.return_value
        assert fh.write.call_count == 1
        assert fh.write.call_args == mock.call(conf_str)

    def test_input_wrapper(self):
        dc = DnstestConfig()
        input_mock = mock.MagicMock()
        if sys.version_info[0] == 3:
            with mock.patch('builtins.input', input_mock):
                dc.input_wrapper("foo")
        else:
            with mock.patch('__builtin__.raw_input', input_mock):
                dc.input_wrapper("foo")
        assert input_mock.call_count == 1
        assert input_mock.call_args == mock.call('foo')
