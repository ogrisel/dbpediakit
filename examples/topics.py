r"""Use PostgreSQL to extract a taxonomy out of DBpedia categories

The default category tree of DBpedia / Wikipedia has more than 500k categories
most of which are not interesting.

This scripts load the whole tree in a PostgreSQL DB and use several joins to
extract a substree of ~50K interesting topics which focusing on topics that are
related to an resource with a descriptive enough abstract.

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

  $ psql -d dbpediakit
  psql (9.1.2)
  Type "help" for help.

  dbpediakit=#

"""
# Author: Olivier Grisel <olivier.grisel@ensta.org>
# License: MIT

# WARNING: there is no proper escaping but I did not want to introduce a
# dependency on sqlalchemy just for a tiny script, don't use this on a
# production webapplication with untrusted users

import dbpediakit as db
import subprocess as sp

SQL_LIST_TABLES = ("SELECT tablename FROM pg_tables"
                   " WHERE schemaname = 'public';")

DATABASE = "dbpediakit"
PSQL = "psql"


def execute(query, database=DATABASE):
    return sp.call([PSQL, database, "-c", query])


def select(query, database=DATABASE):
    return sp.check_output([PSQL, database, "-qAtc", query])


def copy(tuples, table, database=DATABASE):
    query = "COPY %s FROM STDIN WITH CSV" % table
    p = sp.Popen([PSQL, database, "-c", query], stdin=sp.PIPE)
    db.dump_as_csv(tuples, p.stdin, end_marker="\\.\n")
    assert p.wait() == 0


def check_link_table(archive_name, table, database=DATABASE, **extract_params):
    """Intialize a SQL table to host link tuples from dump"""
    if table in select(SQL_LIST_TABLES):
        return

    query = "CREATE TABLE " + table
    query += " ("
    query += " source varchar(100) NOT NULL,"
    query += " target varchar(100) NOT NULL"
    query += ");"
    execute(query, database=database)

    tuples = db.extract_link(db.fetch(archive_name), **extract_params)
    copy(tuples, table, database=database)


if __name__ == "__main__":
    max_items = 100  # set to None for processing the complete dumps

    # Ensure the data is cached locally or download it from the dbpedia.org
    # site

    long_abstracts = db.extract_text(
        db.fetch("long_abstracts"),
        max_items=max_items)

    check_link_table(
        "redirects", "redirects",
        predicate_filter="http://dbpedia.org/ontology/wikiPageRedirects",
        max_items=max_items)

    check_link_table(
        "skos_categories", "skos_categories",
        predicate_filter="http://www.w3.org/2004/02/skos/core#broader",
        max_items=max_items)

#    import sys
#    db.dump_as_csv(skos_categories, sys.stdout)
#    db.dump_as_csv(redirects, sys.stdout)
