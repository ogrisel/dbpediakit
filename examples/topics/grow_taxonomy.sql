-- Script to traverse the broader to narrower graph from some roots to grow one
-- more layer in the taxonomy DAG.

-- Author: Olivier Grisel <olivier.grisel@ensta.org>
-- License: MIT

INSERT INTO taxonomy_dag
SELECT gc.id, gc.article, td.depth + 1, td.path || gc.id,
CASE WHEN gc.grounded THEN td.grounded_path || gc.id ELSE td.grounded_path END
FROM grounded_categories gc, taxonomy_dag td
WHERE gc.broader = td.id
AND td.depth = (select max(depth) from taxonomy_dag)
AND NOT td.path && ARRAY[gc.id];
