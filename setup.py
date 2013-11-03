from distutils.core import setup
from sys import version_info
from pydnstest.version import VERSION

# different requirements for py2x and py3x
# will this work right? I have no idea...
if version_info.major == 3:
    pyver_requires = [
        "py3dns==3.0.4",
        "pyparsing==2.0.1",
    ]
else:
    pyver_requires = [
        "pydns==2.3.6",
        "pyparsing==1.5.7",
    ]

setup(
    name='pydnstest',
    version=VERSION,
    author='Jason Antman',
    author_email='jason@jasonantman.com',
    packages=['pydnstest', 'pydnstest.tests'],
    scripts=['bin/pydnstest'],
    url='http://github.com/jantman/pydnstest/',
    license='LICENSE.txt',
    description='Tool to test DNS changes on a staging server and verify in production',
    long_description='Python tool for testing DNS changes (add, remove, rename, change records) against a staging DNS server, verifying the same changes against production, or confirming that a record returns the same result in both environments.',
    install_requires=pyver_requires
)
