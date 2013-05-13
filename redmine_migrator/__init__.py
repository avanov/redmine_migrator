import argparse


def main():
    """
    CLI entry point
    """
    cli_parser = argparse.ArgumentParser(
        description='Migrate Redmine data from SQLite to Postgres'
    )
    cli_parser.add_argument('sqlite_url', help="SQLite source URL")
    cli_parser.add_argument('postgres_url', help="Postgres target URL")
    conf = cli_parser.parse_args()

