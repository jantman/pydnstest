"""
Logic for checking desired DNS configuration against actual configuration
on prod and test servers.
"""

from dnstest_dns import DNStestDNS


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

        # resolve with both test and prod
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
            rev = self.DNS.lookup_reverse(qp['answer']['data'], self.config.server_test)
            if 'answer' in rev:
                res['warnings'].append("%s appears to still have reverse DNS set to %s (TEST)" % (n, rev['answer']['data']))
        elif 'status' in qt:
            res['result'] = False
            res['message'] = "%s returned status %s (TEST)" % (n, qt['status'])
        else:
            res['result'] = False
            res['message'] = "%s returned valid answer, not removed (TEST)" % n
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

        # resolve with both test and prod
        qt = self.DNS.resolve_name(name, self.config.server_test)
        qp = self.DNS.resolve_name(name, self.config.server_prod)

        if 'status' in qp and qp['status'] == "NXDOMAIN":
            res['result'] = True
            res['message'] = "%s removed, got status NXDOMAIN (PROD)" % (n)
            # check for any leftover reverse lookups
            rev = self.DNS.lookup_reverse(n, self.config.server_prod)
            if 'answer' in rev:
                res['warnings'].append("%s appears to still have reverse DNS set to %s (PROD)" % (n, rev['answer']['data']))
            rev = self.DNS.lookup_reverse(name, self.config.server_prod)
            if 'answer' in rev:
                res['warnings'].append("%s appears to still have reverse DNS set to %s (PROD)" % (name, rev['answer']['data']))
            elif 'answer' in qt:
                res['secondary'] = ["%s returned answer %s (TEST)" % (n, qt['answer']['data'])]
        elif 'status' in qp and qp['status'] != "NXDOMAIN":
            res['result'] = False
            res['message'] = "%s returned a 'strange' status of %s (PROD)" % (n, qp['status'])
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
                        res['secondary'].append("reverse DNS is set correctly for %s (TEST)" % qt['answer']['data'])
                    else:
                        res['warnings'].append("%s appears to still have reverse DNS set to %s (TEST)" % (n, rev['answer']['data']))
                else:
                    res['warnings'].append("no reverse DNS appears to be set for %s (TEST)" % qt['answer']['data'])
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
                        res['secondary'].append("reverse DNS is set correctly for %s (TEST)" % qt['answer']['data'])
                    else:
                        res['warnings'].append("%s appears to still have reverse DNS set to %s (TEST)" % (newn, rev['answer']['data']))
                else:
                    res['warnings'].append("no reverse DNS appears to be set for %s (TEST)" % qt['answer']['data'])
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
            if qt['answer']['typename'] == 'A' or qp['answer']['typename'] == 'A':
                rev = self.DNS.lookup_reverse(qt['answer']['data'], self.config.server_test)
                if 'answer' in rev:
                    if rev['answer']['data'] == name or rev['answer']['data'] == n:
                        res['secondary'].append("REVERSE OK: %s => %s (TEST)" % (qt['answer']['data'], rev['answer']['data']))
                    else:
                        res['warnings'].append("REVERSE NG: %s appears to still have reverse DNS set to %s (TEST)" % (n, rev['answer']['data']))
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
            rev = self.DNS.lookup_reverse(qp['answer']['data'], self.config.server_prod)
            if 'answer' in rev:
                if rev['answer']['data'] == newval or rev['answer']['data'] == val:
                    res['secondary'].append("reverse DNS is set correctly for %s (PROD)" % qp['answer']['data'])
                else:
                    res['warnings'].append("%s appears to still have reverse DNS set to %s (PROD)" % (n, rev['answer']['data']))
            else:
                res['warnings'].append("no reverse DNS appears to be set for %s (PROD)" % qp['answer']['data'])
        else:
            res['result'] = False
            res['message'] = "change %s to %s failed, resolved to %s (PROD)" % (n, val, qp['answer']['data'])
        return res
