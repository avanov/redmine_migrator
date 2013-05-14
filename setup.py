import os

from setuptools import find_packages
from setuptools import setup


readme = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

setup(
    name='redmine_migrator',
    version='0.1',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'psycopg2',
        'sqlalchemy'
    ],
    setup_requires=['nose'],
    tests_require=['coverage'],
    package_data={
        # If any package contains listed files, include them
        '':['*.txt', '*.rst']
    },
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'redmine_migrator = redmine_migrator:main',
            ]
    },
    # PyPI metadata
    # Read more on http://docs.python.org/distutils/setupscript.html#meta-data
    author="Maxim Avanov",
    author_email="maxim.avanov@gmail.com",
    maintainer="Maxim Avanov",
    maintainer_email="maxim.avanov@gmail.com",
    description="Migrate Redmine data from SQLite to Postgres",
    long_description=readme,
    license="MIT",
    url="https://github.com/2nd/redmine_migrator",
    download_url="https://github.com/2nd/redmine_migrator",
    keywords="cli utils redmine migrate sqlite postgres",
    # See the full list on http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'License :: OSI Approved',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
        'Operating System :: Microsoft',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        ]
)
