#!/usr/bin/env python

"""
Define our initial grammars:

'add (record|name|entry)? <hostname_or_fqdn> (with ?)(value|address|target)? <hostname_fqdn_or_ip>'
'remove (record|name|entry)? <hostname_or_fqdn>'
'rename (record|name|entry)? <hostname_or_fqdn> to <hostname_or_fqdn>'
'change (record|name|entry)? <hostname_or_fqdn> to <hostname_fqdn_or_ip>'

"""

from pyparsing import Word, alphas, alphanums, Suppress, Optional, Or, Regex, Literal, Keyword


class DnstestParser:
    """
    Parses natural-language-like grammar describing DNS changes
    """

    # implement my grammar
    word = Word(alphas)
    value = Word(alphanums).setResultsName("value")
    add_op = Keyword("add").setResultsName("operation")
    rm_op = Keyword("remove").setResultsName("operation")
    rename_op = Keyword("rename").setResultsName("operation")
    change_op = Keyword("change").setResultsName("operation")
    rec_op = Or([Keyword("record"), Keyword("entry"), Keyword("name")])
    val_op = Optional(Keyword("with")) + Or([Keyword("value"), Keyword("address"), Keyword("target")])

    fqdn = Regex("(([a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])(\.([a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9]))*)")
    ipaddr = Regex("((([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}(1[0-9]{2}|2[0-4][0-9]|25[0-5]|[0-9]|[1-9][0-9]))")
    hostname = Regex("([a-zA-Z0-9][a-zA-Z0-9\-]{0,62}[a-zA-Z0-9])")
    hostname_or_fqdn = Or([hostname, fqdn])
    hostname_fqdn_or_ip = Or([hostname, fqdn, ipaddr])

    cmd_add = add_op + Optional(rec_op) + hostname_or_fqdn.setResultsName("hostname") + val_op + hostname_fqdn_or_ip.setResultsName('value')
    cmd_remove = rm_op + Optional(rec_op) + hostname_or_fqdn.setResultsName("hostname")
    cmd_rename = rename_op + Suppress(Optional(rec_op)) + hostname_or_fqdn.setResultsName("hostname") + Suppress(Keyword("to")) + hostname_or_fqdn.setResultsName('value')
    cmd_change = change_op + Suppress(Optional(rec_op)) + hostname_or_fqdn.setResultsName("hostname") + Suppress(Keyword("to")) + hostname_fqdn_or_ip.setResultsName('value')

    line_parser = Or([cmd_add, cmd_remove, cmd_rename, cmd_change])

    def __init__(self):
        pass

    def parse_line(self, line):
        res = self.line_parser.parseString(line, parseAll=True)
        return res
