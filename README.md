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

* git clone
* virtualenv2 pydnstest
* cd pydnstest && source bin/activate
* pip install requirements.txt

Usage
-----
Right now, just edit the config constants and dictionary in example_dns_test.py and then run that file.

ToDo
----
* Move config constants from example_dns_test.py to a dot file or command-line options
* Add natural language processing for input data, then remove example_dns_test.py and just run pydnstest.py
* Add interactive mode for DNS testing
