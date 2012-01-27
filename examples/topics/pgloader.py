"""Use PostgreSQL to extract a taxonomy out of DBpedia categories

Running this script will probably take around 30 minutes.

"""
# Author: Olivier Grisel <olivier.grisel@ensta.org>
# License: MIT

from dbpediakit.postgres import check_link_table
from dbpediakit.postgres import check_text_table

max_items = None  # set to None for processing the complete dumps


def candidate_article_processor(tuples):
    for source, target in tuples:
        yield (source, target, source[len("Category:"):])


check_link_table(
    "redirects", "redirects",
    predicate_filter="http://dbpedia.org/ontology/wikiPageRedirects",
    max_items=max_items)

check_link_table(
    "skos_categories", "categories",
    predicate_filter="http://www.w3.org/2004/02/skos/core#broader",
    columns=(
        ('id', True),
        ('broader', True),
        ('candidate_article', True),
    ),
    processor=candidate_article_processor,
    max_items=max_items)

check_link_table(
    "article_categories", "article_categories",
    predicate_filter="http://purl.org/dc/terms/subject")

check_text_table("long_abstracts", "long_abstracts", max_items=max_items)
