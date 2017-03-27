from setuptools import setup, find_packages


setup(
    name='tsammalex',
    version='0.0',
    description='tsammalex',
    long_description='',
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author='Robert Forkel, MPI SHH',
    author_email='forkel@shh.mpg.de',
    url='https://github.com/clld/tsammalex',
    keywords='web pyramid pylons',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'clld>=3.2.5',
        'clldmpg>=2.0.0',
        'python-docx',
        'pycountry',
    ],
    tests_require=[
        'WebTest >= 1.3.1',  # py3 compat
        'mock>=2.0',
    ],
    test_suite="tsammalex",
    entry_points="""\
[paste.app_factory]
main = tsammalex:main
""")
