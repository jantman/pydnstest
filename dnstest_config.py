"""
configuration logic for dnstest
"""


import os.path
import sys


def find_config_file():
    """
    Returns the absolute path to the dnstest config file, or
    None if no config file is found.

    Looks first for ./dnstest.conf then for ~/.dnstest.conf
    """
    if os.path.exists("dnstest.conf"):
        return os.path.abspath("dnstest.conf")
    if os.path.exists(os.path.expanduser("~/.dnstest.conf")):
        return os.path.abspath(os.path.expanduser("~/.dnstest.conf"))
    sys.stderr.write("WARNING: no config file found. copy dnstest.conf.example to dnstest.conf or ~/.dnstest.conf.\n")
    return True
