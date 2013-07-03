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
val_op = Or([Suppress("value"), Suppress("address"), Suppress("target")])

fqdn = Regex("([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])(\.([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9]))*")
ipaddr = Regex("(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])")
hostname = Regex("([a-zA-Z0-9][a-zA-Z0-9\-]{0,62}[a-zA-Z0-9])")

cmd_add = add_op + hostname.setResultsName("hostname") + val_op + value

tests = []
tests.append("add fooHostOne value fooHostTwo")

def parse_line(line):
    res = cmd_add.parseString(t, parseAll=True)
    return res

for t in tests:
    print t
    r = parse_line(t)
    print r.dump()

# up to slide 27 http://www.slideshare.net/Siddhi/creating-domain-specific-languages-in-python
