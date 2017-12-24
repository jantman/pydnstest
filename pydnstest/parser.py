"""
Input line parsing for pydnstest.

The latest version of this package is available at:
<https://github.com/jantman/pydnstest>

##################################################################################
Copyright 2013-2017 Jason Antman <jason@jasonantman.com>

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

from pyparsing import Word, alphas, alphanums, Suppress, Optional, Or, Regex, Literal, Keyword, MatchFirst, And, NotAny, ParseResults


class DnstestParser:
    """
    Parses natural-language-like grammar describing DNS changes
    """

    grammar_strings = []

    # implement my grammar
    word = Word(alphas)
    value = Word(alphanums).setResultsName("value")
    add_op = Keyword("add").setResultsName("operation")
    rm_op = Keyword("remove").setResultsName("operation")
    rename_op = Keyword("rename").setResultsName("operation")
    change_op = Keyword("change").setResultsName("operation")
    confirm_op = Keyword("confirm").setResultsName("operation")
    rec_op = Or([Keyword("record"), Keyword("entry"), Keyword("name")])
    val_op = Optional(Keyword("with")) + Or([Keyword("value"), Keyword("address"), Keyword("target")])

    fqdn = Regex("(([a-zA-Z0-9_\-]{0,62}[a-zA-Z0-9])(\.([a-zA-Z0-9_\-]{0,62}[a-zA-Z0-9]))*)")
    ipaddr = Regex("((([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}(1[0-9]{2}|2[0-4][0-9]|25[0-5]|[1-9][0-9]|[0-9]))")
    hostname = Regex("([a-zA-Z0-9_\-]{0,62}[a-zA-Z0-9])")
    hostname_or_fqdn = And([NotAny(ipaddr), MatchFirst([fqdn, hostname])])
    hostname_fqdn_or_ip = MatchFirst([ipaddr, fqdn, hostname])

    grammar_strings.append('add (record|name|entry)? <hostname_or_fqdn> (with ?)(value|address|target)? <hostname_fqdn_or_ip>')
    cmd_add = add_op + Optional(rec_op) + hostname_or_fqdn.setResultsName("hostname") + Suppress(val_op) + hostname_fqdn_or_ip.setResultsName('value')

    grammar_strings.append('remove (record|name|entry)? <hostname_or_fqdn>')
    cmd_remove = rm_op + Optional(rec_op) + hostname_fqdn_or_ip.setResultsName("hostname")

    grammar_strings.append('rename (record|name|entry)? <hostname_or_fqdn> (with ?)(value ?) <value> to <hostname_or_fqdn>')
    cmd_rename = rename_op + Suppress(Optional(rec_op)) + hostname_or_fqdn.setResultsName("hostname") + Suppress(Optional(val_op)) + hostname_fqdn_or_ip.setResultsName('value') + Suppress(Keyword("to")) + hostname_or_fqdn.setResultsName('newname')

    grammar_strings.append('change (record|name|entry)? <hostname_or_fqdn> to <hostname_fqdn_or_ip>')
    cmd_change = change_op + Suppress(Optional(rec_op)) + hostname_or_fqdn.setResultsName("hostname") + Suppress(Keyword("to")) + hostname_fqdn_or_ip.setResultsName('value')

    grammar_strings.append('confirm (record|name|entry)? <hostname_or_fqdn>')
    cmd_confirm = confirm_op + Suppress(Optional(rec_op)) + hostname_or_fqdn.setResultsName("hostname")

    line_parser = Or([cmd_confirm, cmd_add, cmd_remove, cmd_rename, cmd_change])

    def __init__(self):
        pass

    def parse_line(self, line):
        res = self.line_parser.parseString(line, parseAll=True)
        d = res.asDict()
        # hostname_or_fqdn using And and NotAny now returns a ParseResults object instead of a string,
        # we need to convert that to a string to just take the first value
        for i in d:
            if isinstance(d[i], ParseResults):
                d[i] = d[i][0]
        return d

    def get_grammar(self):
        """ return a list of possible grammar options """
        return self.grammar_strings
