"""
configuration logic for dnstest
"""


import os.path
import sys
import ConfigParser


def find_config_file():
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


def get_config(conf_file):
    """
    Read configuration from a specified file, return config dict

    :param conf_file: String, absolute path to the conf file to read.
    """
    Config = ConfigParser.ConfigParser()
    Config.read(conf_file)
    conf = {}
    for sec in Config.sections():
        options = Config.options(sec)
        conf[sec] = {}
        for opt in options:
            try:
                conf[sec][opt] = Config.get(sec, opt)
                if conf[sec][opt] in ['True', 'False', 'true', 'false', 'Yes', 'yes', 'No', 'no', '1', '0', 'on', 'On', 'off', 'Off']:
                    conf[sec][opt] = Config.getboolean(sec, opt)
            except:
                conf[sec][opt] = None
    return conf
