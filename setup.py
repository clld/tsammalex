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
        'clld~=4.0',
        'clldmpg~=3.1',
        'python-docx',
        'sqlalchemy',
        'pycountry>=16.11.8',
        'waitress',
    ],
    extras_require={
        'dev': [
            'flake8',
            'psycopg2',
            'tox',
        ],
        'test': [
            'mock',
            'pytest>=3.1',
            'pytest-clld',
            'pytest-mock',
            'pytest-cov',
            'coverage>=4.2',
            'selenium',
            'zope.component>=3.11.0',
        ],
    },
    test_suite="tsammalex",
    entry_points="""\
[paste.app_factory]
main = tsammalex:main
""")
