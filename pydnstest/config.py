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

# conditional imports for packages with different names in python 2 and 3
if sys.version_info[0] == 3:
    import configparser as ConfigParser
else:
    import ConfigParser


class DnstestConfig():

    server_prod = ""
    server_test = ""
    have_reverse_dns = True
    default_domain = ""
    ignore_ttl = False
    sleep = 0.0

    def __init__(self):
        """
        init and setup default values
        """
        pass

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
