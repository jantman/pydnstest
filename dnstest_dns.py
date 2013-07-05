"""
DNS lookup methods for dnstest.py

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
