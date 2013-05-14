redmine_migrator
================

.. image:: https://travis-ci.org/2nd/redmine_migrator.png

Migrate Redmine data from SQLite to Postgres.


Installation
--------------

.. code-block:: bash

    $ virtualenv ~/venv/migrator
    $ source ~/venv/migrator/bin/activate
    $ git clone https://github.com/2nd/redmine_migrator.git ~/projects/migrator
    $ cd ~/projects/migrator
    $ python setup.py develop


Run tests
--------------

.. code-block:: bash

    $ python setup.py nosetests


Usage
--------------

.. code-block:: bash

    $ redmine_migrator sqlite:////path/to/sqlite_redmine.db postgresql+psycopg2://user:password@:port/dbname?host=/var/run/postgresql

