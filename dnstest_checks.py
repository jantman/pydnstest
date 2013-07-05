"""
Logic for checking desired DNS configuration against actual configuration
on prod and test servers.
"""

from dnstest_dns import resolve_name, lookup_reverse


def check_removed_names(removed):
    """
    Run tests for removed names
    """
    for n in removed:
        print
        name = n
        # make sure we have a FQDN
        if name.find('.') == -1:
            name = name + config['defaults']['domain']

        # resolve with both test and prod
        qt = resolve_name(name, config['servers']['test'])
        qp = resolve_name(name, config['servers']['prod'])
        if 'status' in qp:
            print "NG: %s got status %s from PROD - cannot remove a name that doesn't exist (PROD)" % (n, qp['status'])
            continue
        # else we got an answer, it's there, just look for removal

        if 'status' in qt and qt['status'] == "NXDOMAIN":
            print "OK: %s removed, got status NXDOMAIN (TEST)" % (n)
            print "\tPROD value was %s (PROD)" % qp['answer']['data']
            # check for any leftover reverse lookups
            rev = lookup_reverse(qp['answer']['data'], config['servers']['test'])
            if 'answer' in rev:
                print "WARNING: %s appears to still have reverse DNS set to %s (TEST)" % (n, rev['answer']['data'])
        elif 'status' in qt:
            print "ERROR: %s returned status %s (TEST)" % (n, qt['status'])
        else:
            print "NG: %s returned valid answer, not removed (TEST)" % n
    return


def check_changed_names(changed):
    """
    Run tests for changed names
    """
    for n in changed:
        print
        name = n
        newname = changed[n]
        # make sure we have a FQDN
        if name.find('.') == -1:
            name = name + config['defaults']['domain']
        if newname.find('.') == -1:
            newname = newname + config['defaults']['domain']

        # resolve with both test and prod
        qt = resolve_name(newname, config['servers']['test'])
        qp = resolve_name(name, config['servers']['prod'])
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
                rev = lookup_reverse(qt['answer']['data'], config['servers']['test'])
                if 'answer' in rev:
                    if rev['answer']['data'] == changed[n] or rev['answer']['data'] == newname:
                        print "\tok, reverse DNS is set correctly for %s (TEST)" % qt['answer']['data']
                    else:
                        print "\tWARNING: %s appears to still have reverse DNS set to %s (TEST)" % (n, rev['answer']['data'])
                else:
                    print "\tWARNING: no reverse DNS appears to be set for %s (TEST)" % qt['answer']['data']
    return


def check_added_names(added):
    """
    Run tests for added names
    """
    for n in added:
        print
        name = n
        # make sure we have a FQDN
        if name.find('.') == -1:
            name = name + config['defaults']['domain']

        target = added[n]
        if target.find('.') == -1:
            target = target + config['defaults']['domain']

        # resolve with both test and prod
        qt = resolve_name(name, config['servers']['test'])
        qp = resolve_name(name, config['servers']['prod'])
        # make sure PROD returns NXDOMAIN, since it's a new record
        if 'status' in qp:
            if qp['status'] != 'NXDOMAIN':
                print "NG: prod server returned status %s for name %s (PROD)" % (qp['status'], n)
                continue
        else:
            print "NG: new name %s returned valid result from prod server (PROD)" % n
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
            if config['defaults']['have_reverse_dns'] and qt['answer']['typename'] == 'A':
                rev = lookup_reverse(added[n], config['servers']['test'])
                if 'status' in rev:
                    print "\tREVERSE NG: got status %s for name %s (TEST)" % (rev['status'], added[n])
                elif rev['answer']['data'] == n or rev['answer']['data'] == name:
                    print "\tREVERSE OK: %s => %s (TEST)" % (added[n], rev['answer']['data'])
                else:
                    print "REVERSE NG: got answer %s for name %s (TEST)" % (rev['answer']['data'], added[n])
        else:
            print "NG: status %s for name %s (TEST)" % (qt['status'], n)
    return
