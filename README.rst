pydnstest
=========

.. image:: https://img.shields.io/pypi/v/pydnstest.svg
   :target: https://pypi.python.org/pypi/pydnstest

.. image:: http://jantman-personal-public.s3-website-us-east-1.amazonaws.com/pypi-stats/pydnstest/per-month.svg
   :target: http://jantman-personal-public.s3-website-us-east-1.amazonaws.com/pypi-stats/pydnstest/index.html
   :alt: PyPi downloads

.. image:: https://secure.travis-ci.org/jantman/pydnstest.png?branch=master
   :target: http://travis-ci.org/jantman/pydnstest
   :alt: travis-ci for master branch

.. image:: https://codecov.io/github/jantman/pydnstest/coverage.svg?branch=master
   :target: https://codecov.io/github/jantman/pydnstest?branch=master
   :alt: coverage report for master branch

.. image:: http://www.repostatus.org/badges/latest/inactive.svg
   :alt: Project Status: Inactive – The project has reached a stable, usable state but is no longer being actively developed; support/maintenance will be provided as time allows.
   :target: http://www.repostatus.org/#inactive

Python tool for testing DNS changes (add, remove, rename, change records)
against a staging DNS server, verifying the same changes against production,
or confirming that a record returns the same result in both environments.

pydnstest is licensed under the GNU Affero General Public License version 3.

Requirements
------------

* Python 2.7 or 3.4+ (currently tested with 2.7, 3.4, 3.5, 3.6)
* Python `VirtualEnv <http://www.virtualenv.org/>`_ and ``pip`` (recommended installation method; your OS/distribution should have packages for these)
* *or* the following packages:

  * `pydns <https://pypi.python.org/pypi/pydns>`_ (python2) or `py3dns <https://pypi.python.org/pypi/py3dns>`_ (python3)
  * `pyparsing <https://pypi.python.org/pypi/pyparsing>`_

Installation
------------

It's recommended that you install into a virtual environment (virtualenv /
venv). See the `virtualenv usage documentation <http://www.virtualenv.org/en/latest/>`_
for information on how to create a venv. If you really want to install
system-wide, you can (using sudo).

.. code-block:: bash

    pip install pydnstest

Configuration
-------------

Either run ``pydnstest --promptconfig`` to interactively build and write out a configuration file
(to ``~/.dnstest.ini``) or run ``pydnstest --example-config > ~/.dnstest.ini`` and edit the
resulting file as desired.

You can view your current configuration with the ``--configprint`` option.

Usage
-----

pydnstest takes one or more specifications for DNS changes to be made, in a natural-language-like grammar, and tests a staging DNS server (and optionally verifies against a production/live server once the changes are live). For each specification, it prints out a simple one-line OK/NG summary, and optionally some helpful secondary messages and/or warnings. At the moment, it takes input either on STDIN or read from a file.

The following usage examples all assume that you've installed pydnstest in a
virtualenv located at ``~/venv_dir``. If you installed system-wide, simply
omit the first two lines (``cd ~/venv_dir`` and ``source bin/activate``).

Grammar
^^^^^^^

.. code-block:: bash

    add [record|name|entry] <hostname_or_fqdn> [with ][value|address|target] <hostname_fqdn_or_ip>
    remove [record|name|entry] <hostname_or_fqdn>
    rename [record|name|entry] <hostname_or_fqdn> [with] [value|address|target] <value> to <hostname_or_fqdn>
    change [record|name|entry] <hostname_or_fqdn> to <hostname_fqdn_or_ip>
    confirm <hostname_or_fqdn> (checks that TEST and PROD return identical results)

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

Write a test file with the following content, at ~/inputfile.txt:

.. code-block:: bash

    add record newhost.example.com with address 10.188.8.90
    add record newhost-console.example.com with address 10.188.15.90

And then run the tests on it:

.. code-block:: bash

    jantman@phoenix$ cd ~/venv_dir
    jantman@phoenix$ source bin/activate
    (venv_dir)jantman@phoenix$ pydnstest -f ~/inputfile.txt
    OK: newhost.example.com => 10.188.8.90 (TEST)
            PROD server returns NXDOMAIN for newhost.example.com (PROD)
            REVERSE OK: 10.188.8.90 => newhost.example.com (TEST)
    OK: newhost-console.example.com => 10.188.15.90 (TEST)
            PROD server returns NXDOMAIN for newhost-console.example.com (PROD)
            REVERSE OK: 10.188.15.90 => newhost-console.example.com (TEST)
    ++++ All 2 tests passed. (pydnstest 0.1.0)


Verify once in prod
^^^^^^^^^^^^^^^^^^^

After making the above changes live, verify them in production:

.. code-block:: bash

    jantman@phoenix$ cd ~/venv_dir
    jantman@phoenix$ source bin/activate
    (venv_dir)jantman@phoenix$ pydnstest -f ~/inputfile.txt -V
    OK: newhost.example.com => 10.188.8.90 (PROD)
            REVERSE OK: 10.188.8.90 => newhost.example.com (PROD)
    OK: newhost-console.example.com => 10.188.15.90 (PROD)
            REVERSE OK: 10.188.15.90 => newhost-console.example.com (PROD)
    ++++ All 2 tests passed. (pydnstest 0.1.0)

Run one quick test
^^^^^^^^^^^^^^^^^^

Do a quick one-off test passed in on stdin, to confirm that prod and test
return the same result for a given name:

.. code-block:: bash

    jantman@phoenix$ cd ~/venv_dir
    jantman@phoenix$ source bin/activate
    (venv_dir)jantman@phoenix$ echo "confirm foo.example.com" | pydnstest
    OK: prod and test servers return same response for 'foo.example.com'
        response: {'name': 'foo.example.com', 'data': '10.10.8.2', 'typename': 'A', 'classstr': 'IN', 'ttl': 360, 'type': 1, 'class': 1, 'rdlength': 4}
    ++++ All 1 tests passed. (pydnstest 0.1.0)

Run interactively from STDIN
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can also provide test data on STDIN. This is mainly useful when pulling test data
from another file, such as:

.. code-block:: bash

    jantman@phoenix:pts/12:~/tmp$ cat sample_zone.txt
    $ORIGIN example.com.

    ;PYDNSTEST add record foo.example.com with address 10.10.8.2
    foo       IN     A     10.10.8.2
    ;PYDNSTEST add record bar.example.com with address 10.10.8.3
    bar       IN     A     10.10.8.3
    ;PYDNSTEST add record baz.example.com with address 10.10.8.4
    baz       IN     A     10.10.8.4
    jantman@phoenix$ cd ~/venv_dir
    jantman@phoenix$ source bin/activate
    (venv_dir)jantman@phoenix$ grep "^;PYDNSTEST" ~/tmp/sample_zone.txt | sed 's/^;PYDNSTEST //' | pydnstest
    OK: prod and test servers return same response for 'foo.example.com'
        response: {'name': 'foo.example.com', 'data': '10.10.8.2', 'typename': 'A', 'classstr': 'IN', 'ttl': 360, 'type': 1, 'class': 1, 'rdlength': 4}
    OK: prod and test servers return same response for 'bar.example.com'
        response: {'name': 'bar.example.com', 'data': '10.10.8.3', 'typename': 'A', 'classstr': 'IN', 'ttl': 360, 'type': 1, 'class': 1, 'rdlength': 4}
    OK: prod and test servers return same response for 'baz.example.com'
        response: {'name': 'baz.example.com', 'data': '10.10.8.4', 'typename': 'A', 'classstr': 'IN', 'ttl': 360, 'type': 1, 'class': 1, 'rdlength': 4}
    ++++ All 3 tests passed. (pydnstest 0.2.2)

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

To install for development:

1. Fork the `pydnstest <https://github.com/jantman/pydnstest>`_ repository on GitHub
2. Create a new branch off of master in your fork.

.. code-block:: bash

    $ virtualenv pydnstest
    $ cd pydnstest && source bin/activate
    $ pip install -e git+git@github.com:YOURNAME/pydnstest.git@BRANCHNAME#egg=pydnstest
    $ cd src/pydnstest

The git clone you're now in will probably be checked out to a specific commit,
so you may want to ``git checkout BRANCHNAME``.

Guidelines
----------

* pep8 compliant with some exceptions (see pytest.ini)
* 100% test coverage with pytest (with valid tests) (note that until
  https://github.com/lemurheavy/coveralls-public/issues/31 is fixed, you
  need to check the ``cov`` output for branch coverage, coveralls can't
  be relied on).

Testing
-------

Testing is done via `pytest <http://pytest.org/latest/>`_, driven by `tox <http://tox.testrun.org/>`_
and currently encompasses testing for both the input language parsing, and the
DNS testing logic (via stubbing the DNS lookup methods and returning known
results).

Be aware that the tests also run a few live DNS queries (dnstest_dns_test.py /
TestDNS class) against domains that I control, mostly as a sanity check for
changes in the underlying pydns library. These may occasionally timeout or
fail, as is the case with any live network tests.

* testing is as simple as:

  * ``pip install tox``
  * ``tox``

* If you want to see code coverage: ``tox -e cov``

  * this produces two coverage reports - a summary on STDOUT and a full report in the ``htmlcov/`` directory

* If you want to pass additional arguments to pytest, add them to the tox command line after "--". i.e., for verbose pytext output on py27 tests: ``tox -e py27 -- -v``

Release Checklist
-----------------

1. Open an issue for the release; cut a branch off master for that issue.
2. Confirm that there are CHANGES.rst entries for all major changes.
3. Ensure that Travis tests passing in all environments.
4. Ensure that test coverage is no less than the last release (ideally, 100%).
5. Increment the version number in pydnstest/version.py and add version and release date to CHANGES.rst, then push to GitHub.
6. Confirm that README.rst renders correctly on GitHub.
7. Upload package to testpypi, confirm that README.rst renders correctly.

   * Make sure your ~/.pypirc file is correct
   * ``python setup.py register -r https://testpypi.python.org/pypi``
   * ``python setup.py sdist upload -r https://testpypi.python.org/pypi``
   * Check that the README renders at https://testpypi.python.org/pypi/pydnstest

8. Create a pull request for the release to be merge into master. Upon successful Travis build, merge it.
9. Tag the release in Git, push tag to GitHub:

   * tag the release. for now the message is quite simple: ``git tag -a vX.Y.Z -m 'X.Y.Z released YYYY-MM-DD'``
   * push the tag to GitHub: ``git push origin vX.Y.Z``

11. Upload package to live pypi:

    * ``python setup.py sdist upload``

10. make sure any GH issues fixed in the release were closed.
