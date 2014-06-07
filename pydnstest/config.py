"""
configuration logic for dnstest

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


import os.path
import sys
import re

# conditional imports for packages with different names in python 2 and 3
if sys.version_info[0] == 3:
    import configparser as ConfigParser
else:
    import ConfigParser


class DnstestConfig():

    conf_file = os.path.expanduser("~/.dnstest.ini")  # default value
    server_prod = ""
    server_test = ""
    have_reverse_dns = True
    default_domain = ""
    ignore_ttl = False
    sleep = 0.0

    ipaddr_re = None
    bool_t_re = None
    bool_f_re = None

    def __init__(self):
        """
        init and setup default values
        """
        self.ipaddr_re = re.compile(r'^((([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}(1[0-9]{2}|2[0-4][0-9]|25[0-5]|[1-9][0-9]|[0-9]))$')
        self.bool_t_re = re.compile(r'^(y|yes|t|true|on|1)$', re.IGNORECASE)
        self.bool_f_re = re.compile(r'^(n|no|f|false|off|0)$', re.IGNORECASE)

    def asDict(self):
        """
        return a dictionary of all configuration options.
        """
        d = {'servers': {'prod': self.server_prod, 'test': self.server_test},
             'have_reverse_dns': self.have_reverse_dns, 'default_domain': self.default_domain,
             'ignore_ttl': self.ignore_ttl, 'sleep': 0.0}
        return d

    def find_config_file(self):
        """
        Returns the absolute path to the dnstest config file, or
        None if no config file is found.

        Looks first for ./dnstest.ini then for ~/.dnstest.ini
        """
        if os.path.exists("dnstest.ini"):
            return os.path.abspath("dnstest.ini")
        if os.path.exists(os.path.expanduser("~/.dnstest.ini")):
            return os.path.abspath(os.path.expanduser("~/.dnstest.ini"))
        return None

    def load_config(self, conf_file):
        """
        Read configuration from a specified file, return config dict

        :param conf_file: String, absolute path to the conf file to read.
        """
        Config = ConfigParser.ConfigParser()
        self.conf_file = conf_file
        Config.read(conf_file)

        try:
            self.server_prod = Config.get("servers", "prod")
        except:
            self.server_prod = ""

        try:
            self.server_test = Config.get("servers", "test")
        except:
            self.server_test = ""

        try:
            self.default_domain = Config.get("defaults", "domain")
        except:
            self.default_domain = ""

        try:
            self.have_reverse_dns = Config.getboolean("defaults", "have_reverse_dns")
        except:
            self.have_reverse_dns = True

        try:
            self.ignore_ttl = Config.getboolean("defaults", "ignore_ttl")
        except:
            self.ignore_ttl = False

        try:
            self.sleep = Config.getfloat("defaults", "sleep")
        except:
            self.sleep = 0.0

        return True

    def set_example_values(self):
        """
        Set config contents to example values.
        """
        self.server_prod = '1.2.3.4'
        self.server_test = '1.2.3.5'
        self.have_reverse_dns = True
        self.default_domain = '.example.com'
        self.ignore_ttl = False
        self.sleep = 0.0

    def to_string(self):
        """
        Convert the current configuration to an ini-style string,
        suitable for writing to the config file.

        We do this manually (i.e. without configparser) to preserve comments.
        """
        s = """[servers]
# the IP address of your production/live DNS server
prod: {prod}

# the IP address of your test/staging DNS server
test: {test}

[defaults]
# True if you want to check ofr reverse DNS (for A records) by default, False otherwise
have_reverse_dns: {have_reverse}

# the default domain (i.e. ".example.com") to append to any input which appears to be a hostname (i.e. not a FQDN or an IP address)
domain: {domain}

# True if you want to ignore the 'ttl' attribute when comparing responses from prod and test servers
ignore_ttl: {ignore_ttl}

# a (float) number of seconds to sleep between DNS tests; default 0.0
sleep: {sleep}
""".format(prod=self.server_prod,
           test=self.server_test,
           have_reverse=str(self.have_reverse_dns),
           domain=self.default_domain,
           ignore_ttl=self.ignore_ttl,
           sleep=self.sleep)
        return s

    def write(self):
        """
        write config to file specified by self.conf_file
        """
        # write out the config
        with open(self.conf_file, 'w') as fh:
            fh.write(self.to_string())

    def input_wrapper(self, prompt):
        """
        wrapper to call the correct raw_input/input depending on python version

        see https://docs.python.org/3/whatsnew/3.0.html#builtins
        and http://legacy.python.org/dev/peps/pep-3111/
        """
        if sys.version_info[0] == 3:
            return input(prompt)
        return raw_input(prompt)

    def prompt_config(self):
        """
        interactively prompt the user through generating a configuration file
        and writing it to disk
        """
        # get each of the configuration elements
        self.server_prod = self.prompt_input("Production DNS Server IP", validate_cb=self.validate_ipaddr)
        self.server_test = self.prompt_input("Test/Staging DNS Server IP", validate_cb=self.validate_ipaddr)
        self.have_reverse_dns = self.prompt_input("Check for reverse DNS by default? [Y|n]", default=True, validate_cb=self.validate_bool)
        self.default_domain = self.prompt_input("Default domain for to append to any input that appears to be less than a FQDN (blank for none)", default='')
        self.ignore_ttl = self.prompt_input("Ignore difference in TTL when comparing responses? [y|N]", default=False, validate_cb=self.validate_bool)
        self.sleep = self.prompt_input("Sleep between DNS record tests (seconds)", default=0.0, validate_cb=self.validate_float)

        # display the full configuration string, ask for confirmation
        print("Configuration:\n#####################\n%s\n#####################\n" % self.to_string())
        res = self.confirm_response("Is this configuration correct?")

        if res:
            self.write()
            print("Configuration written to: {fpath}".format(fpath=self.conf_file))
        else:
            raise SystemExit("Exiting on user request. No configuration written.")
        return True

    def prompt_input(self, prompt, default=None, validate_cb=None):
        """
        accept and validate interactive input of an IP addrenss

        validate_cb is a callable that validates and/or munges input.
        it returns None on no or invalid input, or the munged input value on success.

        :param prompt: prompt for the user
        :type prompt: string
        :param default: default value, or None
        :pararm validate_cb: callback function to validate and munge
        :type validate_cb: callable
        """
        prompt_s = "{prompt}: ".format(prompt=prompt)
        if default is not None:
            if default is True:
                default_s = 'y'
            elif default is False:
                default_s = 'n'
            else:
                default_s = "{default}".format(default=default)
            prompt_s = "{prompt:s} (default: {default}): ".format(prompt=prompt, default=default_s)
        result = None
        while result is None:
            response = self.input_wrapper(prompt_s).strip()
            if default is not None and response == '':
                response = default_s
            raw_response = response
            if validate_cb is not None:
                response = validate_cb(response)
            if response is None:
                print("ERROR: invalid response: {resp:s}".format(resp=raw_response))
                continue
            if not self.confirm_response(raw_response):
                continue
            result = response
        return result

    def confirm_response(self, s):
        """ yes/no confirmation of a response """
        r = self.input_wrapper("Is '{response:s}' correct? [y/N] ".format(response=s)).strip()
        if re.match(r'^(yes|y|true|t)$', r, re.IGNORECASE):
            return True
        return False

    def validate_ipaddr(self, s):
        """
        validate string s as an IP address. Return s on success or None on failure

        :param s: string to validate
        :type s: string
        """
        if self.ipaddr_re.match(s):
            return s
        return None

    def validate_bool(self, s):
        """
        validate string s as a boolean value. Return s on success or None on failure

        :param s: string to validate
        :type s: string
        """
        if self.bool_t_re.match(s.strip()):
            return True
        if self.bool_f_re.match(s.strip()):
            return False
        return None

    def validate_float(self, s):
        """
        validate string s as an IP address. Return s on success or None on failure

        :param s: string to validate
        :type s: string
        """
        s = s.strip()
        try:
            f = float(s)
            return f
        except ValueError:
            return None
