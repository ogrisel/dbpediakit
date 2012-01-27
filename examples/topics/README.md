# Python / SQL scripts to build a topic taxonomy from Wikipedia categories

The default category tree of DBpedia / Wikipedia has more than 500k categories
most of which are not interesting.

This script loads the whole tree in a PostgreSQL DB and use several joins to
extract a substree of ~50K interesting topics which focusing on topics that are
related to an resource with a descriptive enough abstract.


## Installing a PostgreSQL database as analytical workspace

We will use PostgreSQL to perform the various joins between articles,
redirects, broader and narrower topics.

To initialize the PostgreSQL under Ubuntu / Debian::

    $ sudo apt-get install postgresql

Then switch to the postgres admin user to create a role and DB for your unix
user and your dbpediakit usage. For instance my unix account is `ogrisel`:

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

If it does not work edit the `/etc/postgresql/x.x/main/pg_hba.conf` file to set
the local users to be identified using the `ident` policy. The restart
postgresql with `sudo service postgresql restart`.


## Loading the category data into the database

This will download the data dumps from DBpedia, parse the RDF and load the
tuples into PostgreSQL tables and create indices on columns involved in joins:

    $ python pgloader.py

This will take around 30 min on a typical macbook pro in total.
