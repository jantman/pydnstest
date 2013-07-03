#!/usr/bin/env python

"""
Define our initial grammars:

'add (record|name|entry)? <hostname_or_fqdn> (with ?)(value|address|target)? <hostname_fqdn_or_ip>'
'remove (record|name|entry)? <hostname_or_fqdn>'
'rename (record|name|entry)? <hostname_or_fqdn> to <hostname_or_fqdn>'
'change (record|name|entry)? <hostname_or_fqdn> to <hostname_fqdn_or_ip>'
'(set )?reverse( for)? (record|name|entry)? <hostname_or_fqdn> to <hostname_or_fqdn>'

"""

from pyparsing import Word, alphas, alphanums, Suppress, Optional, Or

# implement my grammar
word = Word(alphas)
value = Word(alphanums).setResultsName("value")
hostname = word.setResultsName("hostname")
add_op = "add"
val_op = Or([Suppress("value"), Suppress("address"), Suppress("target")])

cmd_add = add_op + hostname + val_op + value

#element = Regex("A[cglmrstu]|B[aehikr]?|C[adeflmorsu]?|D[bsy]|"
#                "E[rsu]|F[emr]?|G[ade]|H[efgos]?|I[nr]?|Kr?|L[airu]|"
#                "M[dgnot]|N[abdeiop]?|Os?|P[abdmortu]?|R[abefghnu]|"
#                "S[bcegimnr]?|T[abcehilm]|Uu[bhopqst]|U|V|W|Xe|Yb?|Z[nr]")

tests = []
tests.append("add fooHostOne value fooHostTwo")

for t in tests:
    print t
    res = cmd_add.parseString(t, parseAll=True)
    print res.dump()

# up to slide 27 http://www.slideshare.net/Siddhi/creating-domain-specific-languages-in-python
