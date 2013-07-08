"""
configuration logic for dnstest
"""


import os.path
import sys
import ConfigParser


class DnstestConfig():


    server_prod = ""
    server_test = ""
    reverse_dns = True
    default_domain = ""


    def __init__(self):
        """
        init and setup default values
        """
        pass

    def asDict(self):
        """
        return a dictionary of all configuration options.
        """
        d = {'servers': {'prod': self.server_prod, 'test': self.server_test}, 'have_reverse_dns': self.reverse_dns, 'default_domain': self.default_domain}
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
            self.reverse_dns = Config.getboolean("defaults", "have_reverse_dns")
        except:
            self.reverse_dns = True

        return True
