#!/usr/bin/env python

"""
Define our initial grammars:

'add (record|name|entry)? <hostname_or_fqdn> (with ?)(value|address|target)? <hostname_fqdn_or_ip>'
'remove (record|name|entry)? <hostname_or_fqdn>'
'rename (record|name|entry)? <hostname_or_fqdn> to <hostname_or_fqdn>'
'change (record|name|entry)? <hostname_or_fqdn> to <hostname_fqdn_or_ip>'
'(set )?reverse( for)? (record|name|entry)? <hostname_or_fqdn> to <hostname_or_fqdn>'

"""

from pyparsing import Word, alphas, alphanums, Suppress, Optional, Or, Regex, Literal

# implement my grammar
word = Word(alphas)
value = Word(alphanums).setResultsName("value")
add_op = Literal("add").setResultsName("operation")
rec_op = Or([Literal("record"), Literal("entry"), Literal("name")])
val_op = Optional(Literal("with")) + Or([Literal("value"), Literal("address"), Literal("target")])

fqdn = Regex("(([a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])(\.([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9]))*)")
ipaddr = Regex("(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])")
hostname = Regex("([a-zA-Z0-9][a-zA-Z0-9\-]{0,62}[a-zA-Z0-9])")
hostname_or_fqdn = Or([hostname, fqdn])
hostname_fqdn_or_ip = Or([hostname, fqdn, ipaddr])

cmd_add = add_op + Optional(rec_op) + hostname_or_fqdn.setResultsName("hostname") + val_op + hostname_fqdn_or_ip.setResultsName('value')

def parse_line(line):
    res = cmd_add.parseString(line, parseAll=True)
    return res

