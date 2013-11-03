pydnstest
=========

Python tool for testing DNS changes (add, remove, rename, change records)
against a staging DNS server, verifying the same changes against production,
or confirming that a record returns the same result in both environments.

pydnstest is licensed under the GNU Affero General Public License version 3.

**Note - while the code is 100% covered by tests, this is a young project, and
I'm not sure that every code path has been executed in a live environment. As
such, until I can confirm that, I'd recommend repeating the same tests
manually for critical applications (like... say... everything in DNS...)**

Requirements
------------

* Python

  * 2.4 - unknown
  * 2.6 - unknown
  * 2.7 - fully supported (most development is on 2.7)
  * 3.1 - unknown
  * 3.2 - tests pass
  * 3.3 - unknown

* Python `VirtualEnv <http://www.virtualenv.org/>`_ and ``pip`` (recommended installation method; your OS/distribution should have packages for these)
* *or* the following packages:

  * `pydns <https://pypi.python.org/pypi/pydns>`_ (python2) or `py3dns <https://pypi.python.org/pypi/py3dns>`_ (python3)
  * `pyparsing <https://pypi.python.org/pypi/pyparsing>`_

Installation
------------

It's recommended that you clone the git repository and install into a virtual environment.
If you want to install some other way, that's fine, but you'll have to figure it out on your own.

.. code-block:: shell

    git clone https://github.com/jantman/pydnstest.git
    virtualenv pydnstest
    cd pydnstest && source bin/activate
    pip install -r requirements.txt

pip installation should be coming soon...

Configuration
-------------

Copy ``dnstest.ini.example`` to ``~/.dnstest.ini`` (or another
location, which you can tell dnstest about with the ``-f /path/to/dnstest.ini`` option) and open
it in a text editor. Change the values of the following attributes to the
correct ones for your environment (this is an ini-style file, parsed with
Python's ConfigParser module):

* in the ``[servers]`` section:

  * ``prod``: the IP of your production/live DNS server
  * ``test``: the IP of your test/staging DNS server

* in the ``[defaults]`` section:

  * ``have_reverse_dns``: True if you want to check for reverse DNS by default, False otherwise
  * ``domain``: the default domain (i.e. ".example.com") to append to any input which appears to be a hostname (i.e. not a FQDN or an IP address)

Usage
-----

pydnstest takes one or more specifications for DNS changes to be made, in a natural-language-like grammar, and tests a staging DNS server (and optionally verifies against a PROD server once the changes are live). For each specification, it prints out a simple one-line OK/NG summary, and optionally some helpful secondary messages and/or warnings. At the moment, it takes input either on STDIN or read from a file, but will soon also support interactive testing.

Grammar
^^^^^^^

* add [record|name|entry] \<hostname_or_fqdn\> [with ][value|address|target] \<hostname_fqdn_or_ip\>
* remove [record|name|entry] \<hostname_or_fqdn\>'
* rename [record|name|entry] \<hostname_or_fqdn\> [with] [value|address|target] \<value\> to \<hostname_or_fqdn\>
* change [record|name|entry] \<hostname_or_fqdn\> to \<hostname_fqdn_or_ip\>
* confirm \<hostname_or_fqdn\> (checks that TEST and PROD return identical results)

Sample input file
^^^^^^^^^^^^^^^^^

.. code-block:: bash

    add foo.example.com with address 1.2.3.4
    remove bar.example.com
    rename baz.example.com with value 1.2.3.5 to blam.example.com
    change quux.example.com to 1.2.3.6
    confirm blam.example.com

Usage with input file
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    cd pydnstest
    source bin/activate
    bin/dnstest -f dnstests.txt

Verify once in prod
^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bin/dnstest -V -f dnstests.txt

Read from stdin
^^^^^^^^^^^^^^^

.. code-block:: bash

    cat dnstests.txt | bin/dnstest

Run one quick test
^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    echo "add host.example.com with address 192.168.0.1" | bin/dnstest

Bugs and Feature Requests
-------------------------

Bug reports and feature requests are happily accepted via the `GitHub Issue Tracker <https://github.com/jantman/pydnstest/issues>`_. Pull requests are
welcome. Issues that don't have an accompanying pull request will be worked on
as my time and priority allows.

License
-------

pydnstest is licensed under the `GNU Affero General Public
License <http://www.gnu.org/licenses/agpl-3.0.html>`_ version 3, with the
additional term that the Copyright and Authors attributions may not be removed
or otherwise altered, except to add the Author attribution of a contributor to
the work. (Additional Terms pursuant to Section 7b of the AGPL v3).

I chose AGPL mostly because I want this software to continue to evolve and
benefit from community involvement and improvement.

Development
===========

Installation for development
----------------------------

1. Fork the `pydnstest <https://github.com/jantman/pydnstest>`_ repository on GitHub
2. Create a new branch off of master in your fork.

.. code-block:: bash

    virtualenv pydnstest
    cd pydnstest && source bin/activate
    pip install -e git+git@github.com:YOURNAME/pydnstest.git@BRANCHNAME#egg=pydnstest
    cd src/pydnstest
    pip install -r requirements_test.txt

The git clone you're now in will probably be checked out to a specific commit,
so you may want to ``git checkout BRANCHNAME``.

Guidelines
----------

* pep8 compliant with some exceptions (see pytest.ini)
* 100% test coverage with pytest (with valid tests)

Testing
-------

Testing is done via `pytest <http://pytest.org/latest/>`_ and currently
encompasses testing for both the input language parsing, and the DNS testing
logic (via stubbing the DNS lookup methods and returning known results). 

I'm currently in the process of converting the project to use `tox <http://tox.readthedocs.org/en/latest/#>`_

* ``py.test``
* If you want to see code coverage: ``py.test --cov-report term-missing --cov-report html --cov=.``

  * this produces two coverage reports - a summary on STDOUT and a full report in the ``htmlcov/`` directory

*  If you want to check pep8 compliance: ``py.test --pep8`` (should be done before any pull requests or merges)

ToDo
----

* Add interactive mode for DNS testing - input one line and show result
* Support py26 through py33, maybe even py24 if possible
