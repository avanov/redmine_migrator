import argparse
from collections import OrderedDict
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def main():
    """
    CLI entry point.
    """
    cli_parser = argparse.ArgumentParser(description='Migrate Redmine data from SQLite to Postgres')
    cli_parser.add_argument('sqlite_url', help='SQLite source URL')
    cli_parser.add_argument('postgres_url', help='Postgres target URL')
    cli_parser.add_argument("-v", "--verbose", help='increase output verbosity', action='store_true')
    conf = cli_parser.parse_args()

    if conf.verbose:
        logging.basicConfig()
        logging.getLogger('sqlalchemy').setLevel(logging.INFO)

    # Establish connections
    # ---------------------
    sqlite_engine = create_engine(conf.sqlite_url, encoding='utf-8')
    lite = sessionmaker(bind=sqlite_engine, autocommit=False)()

    postgres_engine = create_engine(conf.postgres_url, encoding='utf-8')
    pg = sessionmaker(bind=postgres_engine, autocommit=False)()

    # Get Postgres' tables info
    # -------------------------
    pg_tables = pg.execute(
        "SELECT table_name "
        "FROM information_schema.tables "
        "WHERE table_schema = 'public' "
        "ORDER BY table_name"
    ).fetchall()
    metadata = []
    for table in pg_tables:
        table_name = table.table_name
        columns = pg.execute(
            "SELECT column_name "
            "FROM information_schema.columns "
            "WHERE table_name = :table_name",
            {'table_name': table_name}
        ).fetchall()
        columns = tuple([column.column_name for column in columns])
        metadata.append((table_name, columns))
    COLUMNS = OrderedDict(metadata)

    sequences = pg.execute("SELECT relname FROM pg_class WHERE relkind = 'S'").fetchall()

    SEQUENCES = set([seq.relname for seq in sequences])

    sqlite_tables = lite.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    SQLITE_TABLES = set([table.name for table in sqlite_tables])

    try:
        missing_tables = []
        for table_name in COLUMNS:
            if table_name not in SQLITE_TABLES:
                missing_tables.append(table_name)
                continue

            records = lite.execute(
                "SELECT * FROM {table_name}".format(table_name=table_name)
            ).fetchall()

            for record in records:
                table_handler = NON_STANDARD_TABLES.get(table_name, handle_standard_table)
                table_handler(pg, table_name, COLUMNS[table_name], record)

            if sequence_name(table_name) in SEQUENCES:
                update_pk_sequence(pg, table_name)

    except Exception:
        pg.rollback()
        raise
    else:
        pg.commit()
    finally:
        lite.close()
        pg.close()


def update_pk_sequence(pgconn, table_name):
    """

    :param pgconn: SQLAlchemy's postgres session instance
    :param str table_name: target table name
    :return: operation status
    :rtype: bool
    """
    current_seq_value = pgconn.execute(
        "SELECT max(id) FROM {table_name}".format(table_name=table_name)
    ).fetchone()[0]
    pgconn.execute(update_pk_sequence_statement(table_name, current_seq_value))
    return True


def insert_statement(table_name, columns, data=None):
    """
    Generates an INSERT statement for given `table_name`.

    :param str table_name: table name
    :param tuple columns: tuple of column names
    :param data: dict of column name => value mapping
    :type data: dict or None
    :return: SQL statement template suitable for sqlalchemy.execute()
    :rtype: str
    """
    data = {} if data is None else data
    columns_list = []
    values_list = []
    for column in columns:
        if column not in data:
            continue
        columns_list.append(column)
        values_list.append(":{column}".format(column=column))

    return (
        "INSERT INTO {table_name} ({columns_list}) "
        "VALUES ({values_list})"
    ).format(
        table_name=table_name,
        columns_list=', '.join(columns_list),
        values_list=', '.join(values_list)
    )


def update_statement(table_name, columns, data=None):
    """
    Generates an UPDATE statement for given `table_name`.

    :param str table_name: table name
    :param tuple columns: tuple of column names
    :param data: dict of column name => value mapping
    :type data: dict or None
    :return: SQL statement template suitable for sqlalchemy.execute()
    :rtype: str
    """
    data = {} if data is None else data
    columns_list = []
    for column in columns:
        if column not in data:
            continue
        columns_list.append("{column} = :{column}".format(column=column))

    return (
        "UPDATE {table_name} SET {columns_list} "
        "WHERE id = :id"
    ).format(
        table_name=table_name,
        columns_list=', '.join(columns_list)
    )


def sequence_name(table_name):
    """
    Generates a standard sequence name of a primary key for a given `table_name`.

    :param str table_name: table name
    :return: sequence name
    :rtype: str
    """
    return '{table_name}_id_seq'.format(table_name=table_name)


def update_pk_sequence_statement(table_name, currval=None):
    """

    :param str table_name: sequence table_name
    :param currval: current value of the sequnece
    :type currval: int or None
    :return:
    :rtype: str
    """
    # currval == None might happen when the target table is empty
    if currval is None:
        currval = 0
    return (
        "ALTER SEQUENCE {sequence_name} RESTART WITH {nextval}"
    ).format(sequence_name=sequence_name(table_name), nextval=currval + 1)


# Handlers
# --------------------------------------

def handle_standard_table(pgconn, table_name, columns, record):
    if 'id' in columns:
        data_exists = pgconn.execute(
            "SELECT 1 FROM {table_name} WHERE id = :id".format(table_name=table_name),
            {'id':record['id']}
        ).fetchone()
        if data_exists:
            pgconn.execute(
                update_statement(table_name, columns, dict(record)),
                record
            )
        else:
            pgconn.execute(
                insert_statement(table_name, columns, dict(record)),
                record
            )
    else:
        pgconn.execute(
            insert_statement(table_name, columns, dict(record)),
            record
        )
    return


def handle_schema_migrations(pgconn, table_name, columns, record):
    """

    :param pgconn:
    :param record: sqlite row record of the corresponding table
    """
    data_exists = pgconn.execute(
        "SELECT 1 FROM schema_migrations WHERE version = :version",
        {'version':record.version}
    ).fetchone()
    if data_exists:
        return
    pgconn.execute("INSERT INTO schema_migrations (version) VALUES (:version)",
        dict(record)
    )
    return


def handle_wiki_content_versions(pgconn, table_name, columns, record):
    #return handle_standard_table(pgconn, table_name, columns, record)
    pass


NON_STANDARD_TABLES = {
    'schema_migrations': handle_schema_migrations,
    'wiki_content_versions': handle_wiki_content_versions
}
