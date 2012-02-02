"""Extract examples of classified articles for machine learning"""

import sys
import os.path
import dbpediakit.postgres as pg


if len(sys.argv) > 1:
    output = "'%s'" % os.path.abspath(sys.argv[1])
else:
    output = "STDOUT"


select_query = """\
SELECT g.id, array_to_string(g.grounded_topics, ' '), la.text
FROM grouped_taxonomy_articles g, long_abstracts la
WHERE g.id = la.id
"""
copy_query = "COPY (%s) TO %s WITH (FORMAT CSV, FORCE_QUOTE *);" % (
    select_query, output)
print copy_query
pg.execute(copy_query)
