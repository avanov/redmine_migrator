redmine_migrator
================

.. image:: https://travis-ci.org/2nd/redmine_migrator.png

Migrate Redmine data from SQLite to Postgres.


Installation
------------

.. code-block:: bash

   $ pip install redmine_migrator


Development version
-------------------

.. code-block:: bash

    $ virtualenv ~/venv/migrator
    $ source ~/venv/migrator/bin/activate
    $ git clone https://github.com/2nd/redmine_migrator.git ~/projects/migrator
    $ cd ~/projects/migrator
    $ python setup.py develop


Tests
--------------


.. code-block:: bash

   $ python setup.py nosetests


Usage
--------------

.. code-block:: bash

   $ redmine_migrator -h
   usage: redmine_migrator [-h] [-v] sqlite_url postgres_url

   Migrate Redmine data from SQLite to Postgres

   positional arguments:
     sqlite_url     SQLite source URL
     postgres_url   Postgres target URL

   optional arguments:
     -h, --help     show this help message and exit
     -v, --verbose  increase output verbosity


Example

.. code-block:: bash

   $ redmine_migrator sqlite:////path/to/sqlite_redmine.db postgresql+psycopg2://user:password@:port/dbname?host=/var/run/postgresql

