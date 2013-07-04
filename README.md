pydnstest
=========

Python script for testing DNS changes (add, remove, change records) against a staging DNS server.

Requirements
------------
* Python2
* pydns from <http://pydns.sourceforge.net/>

Installation
------------
It's recommended that you install into a virtual environment.

* `git clone`
* `virtualenv2 pydnstest`
* `cd pydnstest && source bin/activate`
* `pip install -r requirements.txt`

Usage
-----
To be documented when refactor is done. Will take natural language (well, a
defined natural-language-like grammar) input either read from a file, on
STDIN, or interactively.

Testing
-------
Testing is done via [pytest](http://pytest.org/latest/) and currently
encompasses testing for both the input language parsing, and actual functional
tests of the DNS checks (using two local
[Twisted](http://twistedmatrix.com)-based DNS servers).

* `pip install -r requirements_test.txt`
* py.test

ToDo
----
* Move config constants from example_dns_test.py to a dot file or command-line options
   * ConfigParse for a dotfile or ./dnstest.conf
   * OptParse for command line options
* Add natural language processing for input data, then remove example_dns_test.py and just run pydnstest.py
   * parse_input_line() - iterate over file if specified on command line, or stdin
* Add interactive mode for DNS testing - input one line and show result
* testing for all of the above
* actual testing of DNS to a pair of twisted DNS servers
