"""
pydnstest utility methods

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


def dns_dict_to_string(d):
    """
    returns a key-ordered string representation of a dictionary

    note that this implementation is only intended to work with
    the types that we see in the return dict from our DNS
    query methods.

    starting in python 3.3, by default __hash__() values are
    salted with a random value for security. As a result,
    just running str(dictionary) will produce a non-repeatable
    result. For testing, we need to have the few places that
    include the DNS query result dict in a string to be repeatable.

    @param d dictionary
    @return string
    """
    s = "{"
    for key in sorted(d):
        v = None
        if isinstance(d[key], dict):
            v = dns_dict_to_string(d[key])
        elif isinstance(d[key], str):
            v = "'%s'" % d[key]
        else:
            v = str(d[key])
        s = s + ("'%s': %s, " % (key, v))
    s = s.strip(", ")
    s = s + "}"
    return s
