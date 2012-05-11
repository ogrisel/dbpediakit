"""Use PostgreSQL to extract a taxonomy out of DBpedia categories

Running this script will probably take around 30 minutes.

"""
# Author: Olivier Grisel <olivier.grisel@ensta.org>
# License: MIT

import logging
from os.path import join, sep
import dbpediakit.postgres as pg

SQL_SCRIPTS_FOLDER = __file__.rsplit(sep, 1)[0]


def candidate_article_processor(tuples):
    for source, target in tuples:
        yield (source, target, source[len("Category:"):])


def check_load_taxonomy_data(max_items=None):
    """Load the tables from the source archives

    Leave max_items to None for processing the complete dumps.
    """
    updated = pg.check_link_table(
        "redirects", "redirects",
        predicate_filter="http://dbpedia.org/ontology/wikiPageRedirects",
        max_items=max_items)

    updated &= pg.check_link_table(
        "skos_categories", "categories",
        predicate_filter="http://www.w3.org/2004/02/skos/core#broader",
        columns=(
            ('id', True),
            ('broader', True),
            ('candidate_article', True),
        ),
        processor=candidate_article_processor,
        max_items=max_items)

    updated &= pg.check_link_table(
        "article_categories", "article_categories",
        predicate_filter="http://purl.org/dc/terms/subject")

    if updated:
        pg.execute("ANALYZE")


def check_load_examples_data(max_items):
    """Load the abstract data

    Leave max_items to None for processing the complete dumps.
    """
    updated = pg.check_text_table(
        "long_abstracts", "long_abstracts", max_items=max_items)
    if updated:
        pg.execute("ANALYZE")


def grow_taxonomy(max_depth=1):
    # Load some aggregation function to manipulate arrays of arrays
    # (to materialize paths to the roots in the taxonomy)
    pg.check_run_if_undef(join(SQL_SCRIPTS_FOLDER, "array_aggregate.sql"))

    # Aggregate categories info and find semantic grounding by trying to match
    # with wikipedia articles
    pg.check_run_if_undef(join(SQL_SCRIPTS_FOLDER,
                               "build_grounded_categories.sql"))
    pg.run_file(join(SQL_SCRIPTS_FOLDER, "init_taxonomy.sql"))

    current_depth = int(pg.select("SELECT max(depth) from taxonomy_dag"))
    if current_depth < max_depth:
        for depth in range(current_depth + 1, max_depth + 1):
            logging.info("Growing taxonomy to depth=%d", depth)
            pg.run_file(join(SQL_SCRIPTS_FOLDER, "grow_taxonomy.sql"))


def dump_taxonomy(filename):
    """"""
    query = """\
    SELECT
      d.id,
      string_agg(d.grounded_broader, ' ' ORDER BY d.grounded_broader),
      first_agg(d.article)
    FROM (
      SELECT DISTINCT id, grounded_broader, article
      FROM taxonomy_dag
      WHERE grounded = 't'
    ) AS d
    GROUP BY d.id
    """
    pg.export_to_file(filename, query=query)


def dump_examples(filename, format='tsv'):
    query = """\
    SELECT g.id, array_to_string(g.grounded_topics, ' '), la.text
    FROM grouped_taxonomy_articles g, long_abstracts la
    WHERE g.id = la.id
    """
    pg.export_to_file(filename, query=query)


if __name__ == "__main__":

    import argparse
    all_operations = (
        'build_taxonomy',
        'build_examples',
        'dump_taxonomy',
        'dump_examples',
    )

    parser = argparse.ArgumentParser(
        description='Build a taxonomy and example text documents')

    parser.add_argument(
        '--operations', nargs='+',
        choices=all_operations,
        default=all_operations,
        help='Sequence of operations to execute.')

    parser.add_argument(
        '--taxonomy-file',
        default='dbpedia-taxonomy.tsv',
        help='Filename to store the TSV export of the taxonomy.')

    parser.add_argument(
        '--examples-file', default='dbpedia-examples.tsv.bz2',
        help='Filename to store the TSV export of the examples text'
        ' categorized using the taxonomy.')

    parser.add_argument(
        '--max-depth', default=1, type=int,
        help='Limit the depth of subcategories to follow from the roots.',
    )

    parser.add_argument(
        '--max-items', default=None, type=int,
        help='Limit the number of rows to load from DBpedia archives'
        ' (for debug purpose only)')

    args = parser.parse_args()
    for operation in args.operations:
        if operation == 'build_taxonomy':
            check_load_taxonomy_data(args.max_items)
            grow_taxonomy(args.max_depth)
        elif operation == 'build_examples':
            check_load_examples_data(args.max_items)
            pg.run_file(join(SQL_SCRIPTS_FOLDER, "build_dataset.sql"))
        elif operation == 'dump_taxonomy':
            dump_taxonomy(args.taxonomy_file)
        elif operation == 'dump_examples':
            dump_examples(args.examples_file)
