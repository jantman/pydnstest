Changelog
=========

0.3.0 (2014-06-17)
------------------

* (`issue #6 <https://github.com/jantman/pydnstest/issues/6>`_) add grammar to --help usage output
* add develop branch build status image to README.rst
* update release procedure documentation
* (`issue #12 <https://github.com/jantman/pydnstest/issues/12>`_) add postional argument passthru support for tox to pytest
* got rid of develop branch alltogether - everything on master
* some PEP-8 fixes and test fixes
* added python3 to package classifiers
* added pypi version and download badges to README.rst
* setup coveralls.io for coverage reports
* added missing description of sleep parameter in README.rst
* updated comments in example config to be more clear
* updated README.rst example config to match the one in the package
* added --example-config option to print and example config file and then exit
* added --configprint option to print current config file and then exit
* added mock as a test dependency
* (`issue #7 <https://github.com/jantman/pydnstest/issues/7>`_) added --promptconfig option to interactively build configuration file
* (`issue #20 <https://github.com/jantman/pydnstest/issues/>`_) add warning when reading from stdin
* (`issue #19 <https://github.com/jantman/pydnstest/issues/19>`_) make grammar in usage message come from parser class

0.2.2 (2013-12-07)
------------------

* (`issue #2 <https://github.com/jantman/pydnstest/issues/2>`_) add 'sleep' cli and config file option to sleep X seconds
  between tests
* (`issue #3 <https://github.com/jantman/pydnstest/issues/3>`_) add cli and config option to ignore TTL when comparing
  responses from DNS servers
* (`issue #5 <https://github.com/jantman/pydnstest/issues/5>`_) document release procedure
* (`issue #4 <https://github.com/jantman/pydnstest/issues/4>`_) support one-character hostnames
* (`issue #8 <https://github.com/jantman/pydnstest/issues/8>`_) support leading underscore in hostnames
* add coverage reports to tox and travis-ci
* fix pep8 tests and remove superfluous double test run from tox
* fix coverage report excluded lines
* add test coverage for util module

0.2.1 (2013-11-06)
------------------

* fix README.rst markup error
* add doc parsing tests

0.2.0 (2013-11-06)
------------------

* Documentation updates
* Support py26-py33
* some test fixes for py26-33 support

0.1.0 (2013-11-01)
------------------

* Inital development release
