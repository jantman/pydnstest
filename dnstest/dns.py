"""
DNS lookup methods for dnstest.py - wrapper around the DNS module

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


import DNS


class DNStestDNS:

    def resolve_name(self, query, to_server, to_port=53):
        """
        Resolves a single name against the given server
        """

        # first try an A record
        s = DNS.Request(name=query, server=to_server, qtype='A', port=to_port)
        a = s.req()
        if len(a.answers) > 0:
            return {'answer': a.answers[0]}

        # if that didnt work, try a CNAME
        s = DNS.Request(name=query, server=to_server, qtype='CNAME', port=to_port)
        a = s.req()
        if len(a.answers) > 0:
            return {'answer': a.answers[0]}
        return {'status': a.header['status']}

    def lookup_reverse(self, name, to_server, to_port=53):
        """
        convenience routine for doing a reverse lookup of an address
        """
        a = name.split('.')
        a.reverse()
        b = '.'.join(a) + '.in-addr.arpa'

        s = DNS.Request(name=b, server=to_server, qtype='PTR', port=to_port)
        a = s.req()
        if len(a.answers) > 0:
            return {'answer': a.answers[0]}
        return {'status': a.header['status']}
