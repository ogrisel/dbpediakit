"""Utilities to load tuples from DBpedia to a PostgreSQL database

These utilities use the `psql` commandline client with subprocess and pipe to
communicate with the DB:
 - to avoid introducing a dependency on DB driver
 - to make it possible to bulk load tuples formatted as a CSV stream to the
   DB without using an intermediate file

On the othe hand those utilities do no SQL escaping hence are vulnerable
to SQL injection and should not be deployed on any kind of user facing
server application.

To initialize the PostgreSQL under Ubuntu / Debian::

  $ sudo apt-get install postgresql

Then switch to the postgres admin user to create a role and DB for your unix
user and your dbpediakit usage. For instance my unix account is `ogrisel`::

  $ sudo su - postgres
  $ createuser ogrisel
  Shall the new role be a superuser? (y/n) y
  $ createdb -O ogrisel -E UTF8 dbpediakit
  $ ^D

You can check that database dbpediakit has been created successfully and that
your unix account as access to it with::

  $ psql dbpediakit
  psql (9.1.2)
  Type "help" for help.

  dbpediakit=#

"""
## Author: Olivier Grisel <olivier.grisel@ensta.org>
# License: MIT

# WARNING: there is no proper escaping but I did not want to introduce a
# dependency on sqlalchemy just for a tiny script, don't use this on a
# production webapplication with untrusted users

import subprocess as sp
import dbpediakit.archive as db
import logging

SQL_LIST_TABLES = (
    "SELECT tablename FROM pg_tables"
    " WHERE schemaname = 'public';"
)
SQL_LIST_FUNCTIONS = (
    "SELECT proname from pg_proc p, pg_namespace n"
    " WHERE p.pronamespace = n.oid and n.nspname = 'public';"
)

DATABASE = "dbpediakit"
PSQL = "psql"
PG_COPY_END_MARKER = "\\.\n"  # an EOF "\x04" would also probably work
BUFSIZE = 1024 ** 2
CREATE_INDEX = "CREATE INDEX {table}_{column}_idx ON {table} ({column})"
TABLE_DEF = "-- define tables:"
FUNC_DEF = "-- define functions:"


def run_file(filename, database=DATABASE):
    return sp.call([PSQL, database, "-f", filename])


def check_run_if_undef(filename, database=DATABASE, tables=(), functions=()):
    """Conditionally run SQL script if missing relation or func

    The script is expected to host the matching CREATE TABLE,
    CREATE FUNCTION, CREATE AGGREGATE statements
    """
    defined_tables = set(select(SQL_LIST_TABLES).split())
    defined_functions = set(select(SQL_LIST_FUNCTIONS).split())
    with open(filename, 'r') as sql_script:
        for line in sql_script:
            if line.startswith(TABLE_DEF):
                tables += tuple(
                    t.strip() for t in line[len(TABLE_DEF):].split(","))
            elif line.startswith(FUNC_DEF):
                functions += tuple(
                    f.strip() for f in line[len(FUNC_DEF):].split(","))

    missing_tables = set(tables) - defined_tables
    missing_functions = set(functions) - defined_functions
    no_dependency = not tables and not functions

    if no_dependency or missing_tables or missing_functions:
        logging.info("Running '%s' to define tables %r and functions %r",
                    filename, list(sorted(tables)), list(sorted(functions)))
        code = run_file(filename, database=database)
        if code != 0:
            raise RuntimeError("Failed to execute: " + filename)
        return True
    else:
        logging.info("Skipping sql script '%s'", filename)
        return False


def execute(query, database=DATABASE):
    return sp.call([PSQL, database, "-c", query])


def select(query, database=DATABASE):
    return sp.check_output([PSQL, database, "-qAtc", query])


def copy(tuples, table, database=DATABASE):
    """Pipe the tuples as a CSV stream to a posgresql database table"""
    query = "COPY %s FROM STDIN WITH CSV" % table
    p = sp.Popen([PSQL, database, "-c", query], stdin=sp.PIPE,
                 bufsize=BUFSIZE)
    db.dump_as_csv(tuples, p.stdin, end_marker=PG_COPY_END_MARKER)
    if p.wait() != 0:
        logging.error("Failed to load tuples into %s", table)


def check_link_table(archive_name, table, database=DATABASE,
                     processor=None,
                     columns=(('source', True), ('target', True)),
                     **extract_params):
    """Intialize a SQL table to host link tuples from dump"""
    if table in select(SQL_LIST_TABLES).split():
        logging.info("Table '%s' exists: skipping init from archive '%s'",
                     table, archive_name)
        return False
    logging.info("Loading link table '%s' with tuples from archive '%s'",
                 table, archive_name)

    query = "CREATE TABLE " + table
    query += " ("
    query += ", ".join(column + " varchar(300)" for column, _ in columns)
    query += ");"
    execute(query, database=database)

    tuples = db.extract_link(db.fetch(archive_name), **extract_params)
    if processor is not None:
        tuples = processor(tuples)
    copy(tuples, table, database=database)

    for column, index in columns:
        logging.info("Creating index on column '%s' in table '%s'",
                     column, table)
        execute(CREATE_INDEX.format(table=table, column=column))
    return True


def check_text_table(archive_name, table, database=DATABASE, **extract_params):
    """Intialize a SQL table to host link tuples from dump"""
    if table in select(SQL_LIST_TABLES).split():
        logging.info("Table '%s' exists: skipping init from archive '%s'",
                     table, archive_name)
        return False
    logging.info("Loading text table '%s' with tuples from archive '%s'",
                 table, archive_name)

    query = "CREATE TABLE " + table
    query += " ("
    query += " id varchar(300),"
    query += " title varchar(300),"
    query += " text text,"
    query += " lang char(2)"
    query += ");"
    execute(query, database=database)

    tuples = db.extract_text(db.fetch(archive_name), **extract_params)
    copy(tuples, table, database=database)
    logging.info("Creating index on column '%s' in table '%s'",
                 "id", table)
    execute(CREATE_INDEX.format(table=table, column="id"), database=database)
    return True


def export_as_tsv(table, columns, filename, database=DATABASE):
    """Export the content of a SQL table as tab separated values file"""
    sql = "copy (select %s from %s) TO '%s';" % (
        ', '.join(columns), table, filename)
    execute(sql, database=database)
