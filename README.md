# dbpediakit

Python utilities to do analytics and perform transformations on the
[DBpedia dumps](http://wiki.dbpedia.org/Downloads37).

[DBpedia](http://dbpedia.org) is an extraction of the structured content
of Wikipedia articles (links, redirect, infobox properties) augmented
with a generic ontology (hierarchy of classes for the entities described
by Wikipedia articles and schemas for their properties).

- Author: olivier.grisel@ensta.org
- License: MIT


## Quick example

    >>> import dbpediakit as dbk

    >>> archive_file = dbk.archive.fetch("long_abstracts")
    >>> archive_file
    '/home/ogrisel/data/dbpedia/long_abstracts_en.nt.bz2'

    >>> tuples = dbk.archive.extract_text(archive_file)
    >>> tuples
    <generator object extract_text at 0x41e8aa0></generator>

    >>> first = tuples.next()
    >>> first.id
    Autism

    >>> first.text[:60] + u"..."
    u'Autism is a disorder of neural development characterized by ...'


## Overview

- `dbpediakit.archive` provides lightweight utilities to fetch and
  parse the compressed ntriples (RDF) archive files.

  Parsed content is extracted as generators of python namedtuples.
  Those streams of tuples can then be filtered, processes and serialized to
  file or pipe using the CSV format understood by many databases and ETL.

- `dbpediakit.postgres` provides utilities to load the tuples into a
  PostgreSQL database using the `psql` command line client for efficient
  bulk loading of the parsed data using the `COPY` command from `stdin`.
  The decompressed archive is never fully loaded in memory nor in a
  temporary file but directly streamed to the PostgreSQL database instead.


## Complete examples

- `examples/topics` shows how to process the DBpedia dump to extract
  a topic taxonomy out of the Wikipedia categories useable for document
  classification and navigation.
