"""
Logic for doing the actual DNS result comparisons

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

import re
from pydnstest.dns import DNStestDNS
from pydnstest.util import dns_dict_to_string


class DNStestChecks:
    """
    Methods for checking actual DNS against the desired state.

    Each method returns a dict with the following keys:
    - result: Boolean, True if the test is considered a success, False otherwise
    - message: String, the overall status message, human-readable text
    - secondary: list of strings, describing sub-test steps
    - warnings: list of strings, of any non-critical warnings generated
    {'result': None, 'message': None, 'secondary': [], 'warnings': []}
    """

    config = None
    DNS = None

    def __init__(self, config):
        """
        init method for DNStestChecks - class for all DNS check and verify methods
        """
        self.config = config
        self.DNS = DNStestDNS()
        self.ip_regex = re.compile(r"^((([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}(1[0-9]{2}|2[0-4][0-9]|25[0-5]|[1-9][0-9]|[0-9]))$")

    def check_removed_name(self, n):
        """
        Test a removed name

        @param n name that should be removed
        """
        res = {'result': None, 'message': None, 'secondary': [], 'warnings': []}
        name = n
        # make sure we have a FQDN
        if name.find('.') == -1:
            name = name + self.config.default_domain
        # see if we have an IP address, in which case we're talking about a PTR
        is_ip = False
        if self.ip_regex.match(name):
            is_ip = True

        # resolve with both test and prod
        if is_ip:
            qt = self.DNS.lookup_reverse(name, self.config.server_test)
            qp = self.DNS.lookup_reverse(name, self.config.server_prod)
        else:
            qt = self.DNS.resolve_name(name, self.config.server_test)
            qp = self.DNS.resolve_name(name, self.config.server_prod)

        if 'status' in qp:
            res['result'] = False
            res['message'] = "%s got status %s from PROD - cannot remove a name that doesn't exist (PROD)" % (n, qp['status'])
            return res
        # else we got an answer, it's there, just look for removal

        if 'status' in qt and qt['status'] == "NXDOMAIN":
            res['result'] = True
            res['message'] = "%s removed, got status NXDOMAIN (TEST)" % (n)
            res['secondary'].append("PROD value was %s (PROD)" % qp['answer']['data'])
            # check for any leftover reverse lookups
            if is_ip is False:
                rev = self.DNS.lookup_reverse(qp['answer']['data'], self.config.server_test)
                if 'answer' in rev:
                    if rev['answer']['data'] == name:
                        res['warnings'].append("REVERSE NG: %s appears to still have reverse DNS set to %s (TEST)" % (qp['answer']['data'], rev['answer']['data']))
                    else:
                        res['warnings'].append("REVERSE UNKNOWN: %s appears to still have reverse DNS set, but set to %s (TEST)" % (qp['answer']['data'], rev['answer']['data']))
        elif 'status' in qt:
            res['result'] = False
            res['message'] = "%s returned status %s (TEST)" % (n, qt['status'])
        else:
            res['result'] = False
            res['message'] = "%s returned valid answer of '%s', not removed (TEST)" % (n, qt['answer']['data'])
        return res

    def verify_removed_name(self, n):
        """
        Verify a removed name against the PROD server.

        @param n name that was removed
        """
        res = {'result': None, 'message': None, 'secondary': [], 'warnings': []}
        name = n
        # make sure we have a FQDN
        if name.find('.') == -1:
            name = name + self.config.default_domain
        # see if we have an IP address, in which case we're talking about a PTR
        is_ip = False
        if self.ip_regex.match(name):
            is_ip = True

        # resolve with both test and prod
        if is_ip:
            qt = self.DNS.lookup_reverse(name, self.config.server_test)
            qp = self.DNS.lookup_reverse(name, self.config.server_prod)
        else:
            qt = self.DNS.resolve_name(name, self.config.server_test)
            qp = self.DNS.resolve_name(name, self.config.server_prod)

        if 'status' in qp and qp['status'] == "NXDOMAIN":
            res['result'] = True
            res['message'] = "%s removed, got status NXDOMAIN (PROD)" % (n)
            if 'answer' in qt:
                res['secondary'] = ["%s returned answer %s (TEST)" % (n, qt['answer']['data'])]
        elif 'status' in qp and qp['status'] != "NXDOMAIN":
            res['result'] = False
            res['message'] = "%s returned status %s (PROD)" % (n, qp['status'])
        else:
            res['result'] = False
            res['message'] = "%s returned valid answer of '%s', not removed (PROD)" % (n, qp['answer']['data'])
        return res

    def check_renamed_name(self, n, newn, value):
        """
        Test a renamed name (same value, record name changes)

        @param n old name
        @param newn new name
        @param value the record value (should be unchanged)
        """
        res = {'result': None, 'message': None, 'secondary': [], 'warnings': []}
        name = n
        newname = newn
        newval = value
        # make sure we have a FQDN
        if name.find('.') == -1:
            name = name + self.config.default_domain
        if newname.find('.') == -1:
            newname = newname + self.config.default_domain
        if newval.find('.') == -1:
            newval = newval + self.config.default_domain

        # make sure the old name is gone
        qt_old = self.DNS.resolve_name(name, self.config.server_test)
        if 'answer' in qt_old:
            res['message'] = "%s got answer from TEST (%s), old name is still active (TEST)" % (n, qt_old['answer']['data'])
            res['result'] = False
            return res

        # resolve with both test and prod
        qt = self.DNS.resolve_name(newname, self.config.server_test)
        qp = self.DNS.resolve_name(name, self.config.server_prod)
        if 'status' in qp:
            res['result'] = False
            res['message'] = "%s got status %s from PROD - cannot change a name that doesn't exist (PROD)" % (n, qp['status'])
            return res
        # else we got an answer, it's there, check that it's right

        if 'status' in qt:
            res['result'] = False
            res['message'] = "%s got status %s (TEST)" % (newn, qt['status'])
            return res

        # got valid answers for both, check them
        if qt['answer']['data'] != qp['answer']['data']:
            res['result'] = False
            res['message'] = "%s => %s rename is bad, resolves to %s in TEST and %s in PROD" % (n, newn, qt['answer']['data'], qp['answer']['data'])
        elif qt['answer']['data'] != value and qt['answer']['data'] != newval:
            res['result'] = False
            res['message'] = "%s => %s rename is bad, resolves to %s in TEST (expected value was %s) (TEST)" % (n, newn, qt['answer']['data'], value)
        else:
            # data matches, looks good
            res['result'] = True
            res['message'] = "rename %s => %s (TEST)" % (n, newn)
            # check for any leftover reverse lookups
            if qt['answer']['typename'] == 'A' or qp['answer']['typename'] == 'A':
                rev = self.DNS.lookup_reverse(qt['answer']['data'], self.config.server_test)
                if 'answer' in rev:
                    if rev['answer']['data'] == newn or rev['answer']['data'] == newname:
                        res['secondary'].append("REVERSE OK: reverse DNS is set correctly for %s (TEST)" % qt['answer']['data'])
                    else:
                        res['warnings'].append("REVERSE NG: %s appears to still have reverse DNS set to %s (TEST)" % (qt['answer']['data'], rev['answer']['data']))
                else:
                    res['warnings'].append("REVERSE NG: no reverse DNS appears to be set for %s (TEST)" % qt['answer']['data'])
        return res

    def verify_renamed_name(self, n, newn, value):
        """
        Verify a renamed name (same value, record name changes) against the PROD server.

        @param n original name
        @param newn new name
        @param value the record value (should be unchanged)
        """
        res = {'result': None, 'message': None, 'secondary': [], 'warnings': []}
        name = n
        newname = newn
        newval = value
        # make sure we have a FQDN
        if name.find('.') == -1:
            name = name + self.config.default_domain
        if newname.find('.') == -1:
            newname = newname + self.config.default_domain
        if newval.find('.') == -1:
            newval = newval + self.config.default_domain

        # resolve with both test and prod
        qt = self.DNS.resolve_name(newname, self.config.server_test)
        qp = self.DNS.resolve_name(newname, self.config.server_prod)
        qp_old = self.DNS.resolve_name(name, self.config.server_prod)
        if 'status' in qp:
            res['result'] = False
            res['message'] = "%s got status %s (PROD)" % (newn, qp['status'])
            return res
        if 'answer' in qp_old:
            res['result'] = False
            res['message'] = "%s got answer from PROD (%s), old name is still active (PROD)" % (n, qp_old['answer']['data'])
            return res
        # else we got an answer, it's there, check that it's right

        # got valid answers for both, check them
        if qp['answer']['data'] != value and qp['answer']['data'] != newval:
            res['result'] = False
            res['message'] = "%s => %s rename is bad, resolves to %s in PROD (expected value was %s) (PROD)" % (n, newn, qt['answer']['data'], value)
        else:
            # value matches, old name is gone, looks good
            res['result'] = True
            res['message'] = "rename %s => %s (PROD)" % (n, newn)
            # check for any leftover reverse lookups
            if qp['answer']['typename'] == 'A':
                rev = self.DNS.lookup_reverse(qp['answer']['data'], self.config.server_prod)
                if 'answer' in rev:
                    if rev['answer']['data'] == newn or rev['answer']['data'] == newname:
                        res['secondary'].append("REVERSE OK: reverse DNS is set correctly for %s (PROD)" % qp['answer']['data'])
                    else:
                        res['warnings'].append("REVERSE NG: %s appears to still have reverse DNS set to %s (PROD)" % (qp['answer']['data'], rev['answer']['data']))
                else:
                    res['warnings'].append("REVERSE NG: no reverse DNS appears to be set for %s (PROD)" % qp['answer']['data'])
        return res

    def check_added_name(self, n, value):
        """
        Tests an added name (new record)

        @param n name
        @param value record value
        """
        res = {'result': None, 'message': None, 'secondary': [], 'warnings': []}
        name = n
        # make sure we have a FQDN
        if name.find('.') == -1:
            name = name + self.config.default_domain

        target = value
        if target.find('.') == -1:
            target = target + self.config.default_domain

        # resolve with both test and prod
        qt = self.DNS.resolve_name(name, self.config.server_test)
        qp = self.DNS.resolve_name(name, self.config.server_prod)
        # make sure PROD returns NXDOMAIN, since it's a new record
        if 'status' in qp:
            if qp['status'] != 'NXDOMAIN':
                res['result'] = False
                res['message'] = "prod server returned status %s for name %s (PROD)" % (qp['status'], n)
                return res
        else:
            res['result'] = False
            res['message'] = "new name %s returned valid result from prod server (PROD)" % n
            return res

        # check the answer we got back from TEST
        if 'answer' in qt:
            if qt['answer']['data'] == value or qt['answer']['data'] == target:
                res['result'] = True
                res['message'] = "%s => %s (TEST)" % (n, value)
                res['secondary'].append("PROD server returns NXDOMAIN for %s (PROD)" % n)
            else:
                res['result'] = False
                res['message'] = "%s resolves to %s instead of %s (TEST)" % (n, qt['answer']['data'], value)
                res['secondary'].append("PROD server returns NXDOMAIN for %s (PROD)" % n)
            # check reverse DNS if we say to
            if self.config.have_reverse_dns and qt['answer']['typename'] == 'A':
                rev = self.DNS.lookup_reverse(value, self.config.server_test)
                if 'status' in rev:
                    res['warnings'].append("REVERSE NG: got status %s for name %s (TEST)" % (rev['status'], value))
                elif rev['answer']['data'] == n or rev['answer']['data'] == name:
                    res['secondary'].append("REVERSE OK: %s => %s (TEST)" % (value, rev['answer']['data']))
                else:
                    res['warnings'].append("REVERSE NG: got answer %s for name %s (TEST)" % (rev['answer']['data'], value))
        else:
            res['result'] = False
            res['message'] = "status %s for name %s (TEST)" % (qt['status'], n)
        return res

    def verify_added_name(self, n, value):
        """
        Verify an added name (new record) against the PROD server

        @param n name
        @param value record value
        """
        res = {'result': None, 'message': None, 'secondary': [], 'warnings': []}
        name = n
        # make sure we have a FQDN
        if name.find('.') == -1:
            name = name + self.config.default_domain

        target = value
        if target.find('.') == -1:
            target = target + self.config.default_domain

        # resolve with both test and prod
        qp = self.DNS.resolve_name(name, self.config.server_prod)

        # check the answer we got back from PROD
        if 'answer' in qp:
            if qp['answer']['data'] == value or qp['answer']['data'] == target:
                res['result'] = True
                res['message'] = "%s => %s (PROD)" % (n, value)
            else:
                res['result'] = False
                res['message'] = "%s resolves to %s instead of %s (PROD)" % (n, qp['answer']['data'], value)
            # check reverse DNS if we say to
            if self.config.have_reverse_dns and qp['answer']['typename'] == 'A':
                rev = self.DNS.lookup_reverse(value, self.config.server_prod)
                if 'status' in rev:
                    res['warnings'].append("REVERSE NG: got status %s for name %s (PROD)" % (rev['status'], value))
                elif rev['answer']['data'] == n or rev['answer']['data'] == name:
                    res['secondary'].append("REVERSE OK: %s => %s (PROD)" % (value, rev['answer']['data']))
                else:
                    res['warnings'].append("REVERSE NG: got answer %s for name %s (PROD)" % (rev['answer']['data'], value))
        else:
            res['result'] = False
            res['message'] = "status %s for name %s (PROD)" % (qp['status'], n)
        return res

    def check_changed_name(self, n, val):
        """
        Test a changed name (same record name, new/different value)

        @param n name to change
        @param val new value
        """
        res = {'result': None, 'message': None, 'secondary': [], 'warnings': []}
        name = n
        newval = val
        # make sure we have a FQDN
        if name.find('.') == -1:
            name = name + self.config.default_domain
        if newval.find('.') == -1:
            newval = newval + self.config.default_domain

        # resolve with both test and prod
        qt = self.DNS.resolve_name(name, self.config.server_test)
        qp = self.DNS.resolve_name(name, self.config.server_prod)
        if 'status' in qp:
            res['result'] = False
            res['message'] = "%s got status %s from PROD - cannot change a name that doesn't exist (PROD)" % (n, qp['status'])
            return res
        # else we got an answer, it's there, check that it's right

        if 'status' in qt:
            res['result'] = False
            res['message'] = "%s got status %s (TEST)" % (n, qt['status'])
            return res

        # got valid answers for both, check them
        if qt['answer']['data'] == qp['answer']['data']:
            res['result'] = False
            res['message'] = "%s is not changed, resolves to same value (%s) in TEST and PROD" % (n, qt['answer']['data'])
        elif qt['answer']['data'] != val and qt['answer']['data'] != newval:
            res['result'] = False
            res['message'] = "%s resolves to %s instead of %s (TEST)" % (n, qt['answer']['data'], val)
        else:
            # data matches, looks good
            res['result'] = True
            res['message'] = "change %s from '%s' to '%s' (TEST)" % (n, qp['answer']['data'], qt['answer']['data'])
            # check for any leftover reverse lookups
            if qt['answer']['typename'] == 'A':
                rev = self.DNS.lookup_reverse(qt['answer']['data'], self.config.server_test)
                if 'answer' in rev:
                    if rev['answer']['data'] == name or rev['answer']['data'] == n:
                        res['secondary'].append("REVERSE OK: %s => %s (TEST)" % (qt['answer']['data'], rev['answer']['data']))
                    else:
                        res['warnings'].append("REVERSE NG: %s appears to still have reverse DNS set to %s (TEST)" % (qt['answer']['data'], rev['answer']['data']))
                else:
                    res['warnings'].append("REVERSE NG: no reverse DNS appears to be set for %s (TEST)" % qt['answer']['data'])
        return res

    def verify_changed_name(self, n, val):
        """
        Verify a changed name (same record name, new/different value) against the PROD server

        @TODO - how to verify that the old reverse DNS is removed?

        @param n name to change
        @param val new value
        """
        res = {'result': None, 'message': None, 'secondary': [], 'warnings': []}
        name = n
        newval = val
        # make sure we have a FQDN
        if name.find('.') == -1:
            name = name + self.config.default_domain
        if newval.find('.') == -1:
            newval = newval + self.config.default_domain

        # resolve with both test and prod
        qt = self.DNS.resolve_name(name, self.config.server_test)
        qp = self.DNS.resolve_name(name, self.config.server_prod)
        if 'status' in qp:
            res['result'] = False
            res['message'] = "%s got status %s from PROD (PROD)" % (n, qp['status'])
            return res
        # else we got an answer, it's there, check that it's right

        if 'status' in qt:
            res['result'] = False
            res['message'] = "%s got status %s (TEST)" % (n, qt['status'])
            return res

        # got valid answers for both, check them
        if qp['answer']['data'] == val or qp['answer']['data'] == newval:
            # data matches, looks good
            res['result'] = True
            res['message'] = "change %s value to '%s' (PROD)" % (n, qp['answer']['data'])
            # check for bad reverse DNS
            if qp['answer']['typename'] == 'A':
                rev = self.DNS.lookup_reverse(qp['answer']['data'], self.config.server_prod)
                if 'answer' in rev:
                    if rev['answer']['data'] == n or rev['answer']['data'] == name:
                        res['secondary'].append("REVERSE OK: %s => %s (PROD)" % (qp['answer']['data'], rev['answer']['data']))
                    else:
                        res['warnings'].append("REVERSE NG: %s appears to still have reverse DNS set to %s (PROD)" % (qp['answer']['data'], rev['answer']['data']))
                else:
                    res['warnings'].append("REVERSE NG: no reverse DNS appears to be set for %s (PROD)" % qp['answer']['data'])
        else:
            res['result'] = False
            res['message'] = "%s resolves to %s instead of %s (PROD)" % (n, qp['answer']['data'], val)
        return res

    def confirm_name(self, n):
        """
        Confirms that the given name returns the
        same result in TEST and PROD.

        @param n name
        """
        res = {'result': None, 'message': None, 'secondary': [], 'warnings': []}
        name = n
        # make sure we have a FQDN
        if name.find('.') == -1:
            name = name + self.config.default_domain

        # resolve with both test and prod
        qt = self.DNS.resolve_name(name, self.config.server_test)
        qp = self.DNS.resolve_name(name, self.config.server_prod)
        if 'status' in qt:
            if 'status' not in qp:
                res['message'] = "test server returned status %s for name %s, but prod returned valid answer of %s" % (qt['status'], n, qp['answer']['data'])
                res['result'] = False
                return res
            if qp['status'] == qt['status']:
                res['message'] = "both test and prod returned status %s for name %s" % (qt['status'], n)
                res['result'] = True
                return res
            # else both have different statuses
            res['message'] = "test server returned status %s for name %s, but prod returned status %s" % (qt['status'], n, qp['status'])
            res['result'] = False
            return res
        if 'status' in qp and 'status' not in qt:
            res['message'] = "prod server returned status %s for name %s, but test returned valid answer of %s" % (qp['status'], n, qt['answer']['data'])
            res['result'] = False
            return res

        # remove ttl if we want to ignore it
        if self.config.ignore_ttl:
            qp['answer'].pop('ttl', None)
            qt['answer'].pop('ttl', None)

        # ok, both returned an ansewer. diff them.
        same_res = True
        for k in qt['answer']:
            if k not in qp['answer']:
                res['warnings'].append("NG: test response has %s of '%s'; prod response does not include %s" % (k, qt['answer'][k], k))
                same_res = False
            elif qt['answer'][k] != qp['answer'][k]:
                res['warnings'].append("NG: test response has %s of '%s' but prod response has '%s'" % (k, qt['answer'][k], qp['answer'][k]))
                same_res = False
        for k in qp['answer']:
            if k not in qt['answer']:
                res['warnings'].append("NG: prod response has %s of '%s'; test response does not include %s" % (k, qp['answer'][k], k))
                same_res = False

        # for testing
        res['warnings'] = sorted(res['warnings'])

        if same_res is False:
            res['message'] = "prod and test servers return different responses for '%s'" % n
            res['result'] = False
            return res
        res['message'] = "prod and test servers return same response for '%s'" % n
        res['secondary'].append("response: %s" % dns_dict_to_string(qp['answer']))
        res['result'] = True
        return res
