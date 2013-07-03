#!/usr/bin/env python

"""
Define our initial grammar:

'add <hostname> value <value>'

instr_add ::= add_op hostname val_op val
hostname ::= word
ipaddr ::= numeric+
add_op ::= add
val_op ::= value
value ::= alphanumeric+
word ::= alpha+

"""

from pyparsing import Word, alphas, alphanums

# implement my grammar
word = Word(alphas)
value = Word(alphanums)
hostname = word
add_op = "add"
val_op = Suppress("value")

instr_add = add_op + hostname + val_op + value

print instr_add.parseString("add fooHostOne value fooHostTwo")

# up to slide 27 http://www.slideshare.net/Siddhi/creating-domain-specific-languages-in-python
