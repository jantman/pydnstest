#!/usr/bin/env python
"""
Script to facilitate confirmation of DNS changes on a staging DNS server, comparing to prod.

Requirements:
- pydns from <http://pydns.sourceforge.net/>

See example_dns_test.py for usage - this should be called as a module from that script.

By Jason Antman <jason@jasonantman.com>

ToDo: flag to confirm against prod once live

"""

import DNS


def resolve_name(query, to_server, default_domain, to_port=53):
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


def lookup_reverse(name, to_server, to_port=53):
    "convenience routine for doing a reverse lookup of an address"
    a = name.split('.')
    a.reverse()
    b = '.'.join(a) + '.in-addr.arpa'

    s = DNS.Request(name=b, server=to_server, qtype='PTR', port=to_port)
    a = s.req()
    if len(a.answers) > 0:
        return {'answer': a.answers[0]}
    return {'status': a.header['status']}


def check_removed_names(removed, test_server, prod_server, default_domain, have_reverse):
    """
    Run tests for removed names
    """
    for n in removed:
        print
        name = n
        # make sure we have a FQDN
        if name.find('.') == -1:
            name = name + default_domain

        # resolve with both test and prod
        qt = resolve_name(name, test_server, default_domain)
        qp = resolve_name(name, prod_server, default_domain)
        if 'status' in qp:
            print "NG: %s got status %s from PROD - cannot remove a name that doesn't exist (PROD)" % (n, qp['status'])
            continue
        # else we got an answer, it's there, just look for removal

        if 'status' in qt and qt['status'] == "NXDOMAIN":
            print "OK: %s removed, got status NXDOMAIN (TEST)" % (n)
            print "\tPROD value was %s (PROD)" % qp['answer']['data']
            # check for any leftover reverse lookups
            rev = lookup_reverse(qp['answer']['data'], test_server)
            if 'answer' in rev:
                print "WARNING: %s appears to still have reverse DNS set to %s (TEST)" % (n, rev['answer']['data'])
        elif 'status' in qt:
            print "ERROR: %s returned status %s (TEST)" % (n, qt['status'])
        else:
            print "NG: %s returned valid answer, not removed (TEST)" % n
    return


def check_changed_names(changed, test_server, prod_server, default_domain, have_reverse):
    """
    Run tests for changed names
    """
    for n in changed:
        print
        name = n
        newname = changed[n]
        # make sure we have a FQDN
        if name.find('.') == -1:
            name = name + default_domain
        if newname.find('.') == -1:
            newname = newname + default_domain

        # resolve with both test and prod
        qt = resolve_name(newname, test_server, default_domain)
        qp = resolve_name(name, prod_server, default_domain)
        if 'status' in qp:
            print "NG: %s got status %s from PROD - cannot change a name that doesn't exist (PROD)" % (n, qp['status'])
            continue
        # else we got an answer, it's there, check that it's right

        if 'status' in qt:
            print "NG: %s got status %s (TEST)" % (changed[n], qt['status'])
            continue

        # got valid answers for both, check them
        if qt['answer']['data'] != qp['answer']['data']:
            print "NG: %s => %s rename is bad, resolves to %s in TEST and %s in PROD" % (n, changed[n], qt['answer']['data'], qp['answer']['data'])
        else:
            # data matches, looks good
            print "OK: rename %s => %s (TEST)" % (n, changed[n])
            # check for any leftover reverse lookups
            if qt['answer']['typename'] == 'A' or qp['answer']['typename'] == 'A':
                rev = lookup_reverse(qt['answer']['data'], test_server)
                if 'answer' in rev:
                    if rev['answer']['data'] == changed[n] or rev['answer']['data'] == newname:
                        print "\tok, reverse DNS is set correctly for %s (TEST)" % qt['answer']['data']
                    else:
                        print "\tWARNING: %s appears to still have reverse DNS set to %s (TEST)" % (n, rev['answer']['data'])
                else:
                    print "\tWARNING: no reverse DNS appears to be set for %s (TEST)" % qt['answer']['data']
    return


def check_added_names(added, test_server, prod_server, default_domain, have_reverse):
    """
    Run tests for added names
    """
    for n in added:
        print
        name = n
        # make sure we have a FQDN
        if name.find('.') == -1:
            name = name + default_domain

        target = added[n]
        if target.find('.') == -1:
            target = target + default_domain

        # resolve with both test and prod
        qt = resolve_name(name, test_server, default_domain)
        qp = resolve_name(name, prod_server, default_domain)
        # make sure PROD returns NXDOMAIN, since it's a new record
        if 'status' in qp:
            if qp['status'] != 'NXDOMAIN':
                print "NG: prod server returned status %s for name %s (PROD)" % (qp['status'], n)
                continue
        else:
            print "NG: new name %n returned valid result from prod server (PROD)" % n
            continue

        # check the answer we got back from TEST
        if 'answer' in qt:
            if qt['answer']['data'] == added[n] or qt['answer']['data'] == target:
                print "OK: %s => %s (TEST)" % (n, added[n])
                print "\tPROD server returns NXDOMAIN for %s (PROD)" % n
            else:
                print "NG: %s resolves to %s instead of %s (TEST)" % (n, qt['answer']['data'], added[n])
                print "\tPROD server returns NXDOMAIN for %s (PROD)" % n
            # check reverse DNS if we say to
            if have_reverse and qt['answer']['typename'] == 'A':
                rev = lookup_reverse(added[n], test_server)
                if 'status' in rev:
                    print "\tREVERSE NG: got status %s for name %s (TEST)" % (rev['status'], added[n])
                elif rev['answer']['data'] == n or rev['answer']['data'] == name:
                    print "\tREVERSE OK: %s => %s (TEST)" % (added[n], rev['answer']['data'])
                else:
                    print "REVERSE NG: got answer %s for name %s (TEST)" % (rev['answer']['data'], added[n])
        else:
            print "NG: status %s for name %s (TEST)" % (qt['status'], n)
    return


def do_dns_tests(tests, test_server, prod_server, default_domain, have_reverse=True):
    """
    Run all DNS tests

    param tests: dict with keys 'added',
    """

    if 'added' in tests:
        check_added_names(tests['added'], test_server, prod_server, default_domain, have_reverse)
    if 'removed' in tests:
        check_removed_names(tests['removed'], test_server, prod_server, default_domain, have_reverse)
    if 'changed' in tests:
        check_changed_names(tests['changed'], test_server, prod_server, default_domain, have_reverse)
    return
