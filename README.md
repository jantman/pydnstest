pydnstest
=========

Python script for testing DNS changes (add, remove, rename, change records)
against a staging DNS server, verifying the same changes against production,
or confirming that a record returns the same result in both environments.

Requirements
------------
* Python2 (currently tested with 2.7; other versions coming soon...)
* Python [VirtualEnv](http://www.virtualenv.org/) (your OS/distribution should have packages for these)

Installation
------------
It's recommended that you clone the git repository and install into a virtual environment.
If you want to install some other way, that's fine, but you'll have to figure it out on your own.

```
git clone https://github.com/jantman/pydnstest.git
virtualenv2 pydnstest
cd pydnstest && source bin/activate
pip install -r requirements.txt
```

pip installation should be coming soon...

Configuration
-------------
Copy `dnstest.ini.example` to `dnstest.ini` or `~/.dnstest.ini` (or another
location, which you can tell dnstest.py about with the `-f` option) and open
it in a text editor. Change the values of the following attributes to the
correct ones for your environment (this is an ini-style file, parsed with
Python's ConfigParser module):
* in the [servers] section:
** __prod__: the IP of your production/live DNS server
** __test__: the IP of your test/staging DNS server
* in the [defaults] section:
** __have_reverse_dns__: True if you want to check for reverse DNS by default,
False otherwise
** __domain__: the default domain (i.e. ".example.com") to append to any input
which appears to be a hostname (i.e. not a FQDN or an IP address)

Usage
-----
pydnstest takes one or more specifications for DNS changes to be made, in a natural-language-like grammar, and tests a staging DNS server (and optionally verifies against a PROD server once the changes are live). For each specification, it prints out a simple one-line OK/NG summary, and optionally some helpful secondary messages and/or warnings. At the moment, it takes input either on STDIN or read from a file, but will soon also support interactive testing.

Grammar:
* add [record|name|entry] \<hostname_or_fqdn\> [with ][value|address|target] \<hostname_fqdn_or_ip\>
* remove [record|name|entry] \<hostname_or_fqdn\>'
* rename [record|name|entry] \<hostname_or_fqdn\> [with] [value|address|target] \<value\> to \<hostname_or_fqdn\>
* change [record|name|entry] \<hostname_or_fqdn\> to \<hostname_fqdn_or_ip\>
* confirm \<hostname_or_fqdn\> (checks that TEST and PROD return identical results)

Sample input file:
```
add foo.example.com with address 1.2.3.4
remove bar.example.com
rename baz.example.com with value 1.2.3.5 to blam.example.com
change quux.example.com to 1.2.3.6
confirm blam.example.com
```

Usage with input file:
```
cd pydnstest
source bin/activate
./dnstest.py -f dnstests.txt
```

Verify once in prod:
```
./dnstest.py -V -f dnstests.txt
```

Read from stdin:
```
cat dnstests.txt | ./dnstest.py
```

Run one quick test:
```
echo "add host.example.com with address 192.168.0.1" | ./dnstest.py
```

Development
===========

Installation for development
----------------------------

```
git clone https://github.com/jantman/pydnstest.git
virtualenv2 pydnstest
cd pydnstest && source bin/activate
pip install -r requirements_test.txt
```

Coding Style
------------
* pep8 compliant with some exceptions (see pytest.ini)
* 100% test coverage with pytest

Testing
-------
Testing is done via [pytest](http://pytest.org/latest/) and currently
encompasses testing for both the input language parsing, and the DNS testing
logic (via stubbing the DNS lookup methods and returning known results). 

* `py.test`
* If you want to see code coverage: `py.test --cov-report term-missing --cov-report html --cov=. tests/`
** this produces two coverage reports - a summary on STDOUT and a full report in the htmlcov/ directory
* If you want to check pep8 compliance: `py.test --pep8` (should be done before any pull requests or merges)

ToDo
----
* Add interactive mode for DNS testing - input one line and show result
* Support py26 and py33, maybe even py24 if possible
