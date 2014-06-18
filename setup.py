from setuptools import setup
from sys import version_info
from pydnstest.version import VERSION

if version_info[0] == 3:
    pyver_requires = [
        "py3dns==3.0.4",
        "pyparsing==2.0.1",
    ]
else:
    pyver_requires = [
        "pydns==2.3.6",
        "pyparsing==1.5.7",
    ]

with open('README.rst') as file:
    long_description = file.read()

with open('CHANGES.rst') as file:
    long_description += '\n' + file.read()

classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: System Administrators',
    'Intended Audience :: Information Technology',
    'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
    'Natural Language :: English',
    'Operating System :: POSIX',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Topic :: Internet :: Name Service (DNS)'
]

setup(
    name='pydnstest',
    version=VERSION,
    author='Jason Antman',
    author_email='jason@jasonantman.com',
    packages=['pydnstest', 'pydnstest.tests'],
    scripts=['bin/pydnstest'],
    url='http://github.com/jantman/pydnstest/',
    license='AGPLv3+',
    description='Tool to test DNS changes on a staging server and verify in production',
    long_description=long_description,
    install_requires=pyver_requires,
    keywords="dns testing pydns",
    classifiers=classifiers
)
