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
encompasses testing for both the input language parsing, and the DNS testing
logic (via stubbing the DNS lookup methods and returning known results). 

* `pip install -r requirements_test.txt`
* `py.test`
* If you want to see code coverage: `py.test --cov *.py tests/`
* If you want to check pep8 compliance: `py.test --pep8` (should be done
before any pull requests or merges)

ToDo
----
* Add interactive mode for DNS testing - input one line and show result
* lots more testing
* Figure out how to test command line options - config override
* doctest
