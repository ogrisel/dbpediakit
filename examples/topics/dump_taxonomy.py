"""Extract the taxonmy as a CSV file suitable for Apache Solr / Stanbol"""

import sys
import os.path
import dbpediakit.postgres as pg


if len(sys.argv) > 1:
    output = "'%s'" % os.path.abspath(sys.argv[1])
else:
    output = "STDOUT"


select_query = """\
SELECT d.id, array_to_string(array_agg(d.grounded_broader), ' ') FROM (
  SELECT DISTINCT id, grounded_broader FROM taxonomy_dag WHERE grounded = 't'
) AS d GROUP
BY d.id
"""
copy_query = "COPY (%s) TO %s WITH (FORMAT CSV, FORCE_QUOTE *);" % (
    select_query, output)
print copy_query
pg.execute(copy_query)
