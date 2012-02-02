-- Script to traverse the broader to narrower graph from some roots to build a
-- taxonomy tree (actually a Direct Acyclic Graph).

-- Author: Olivier Grisel <olivier.grisel@ensta.org>
-- License: MIT

-- define tables: taxonomy_dag

DROP TABLE IF EXISTS taxonomy_dag;
CREATE TABLE taxonomy_dag (
    id varchar(300),
    article varchar(300),
    grounded boolean,
    depth integer,
    path varchar(300)[], -- complete path
    grounded_path varchar(300)[], -- subset of the path with
    grounded_broader varchar(300) -- the nearest grounded ancestor or NULL
);

INSERT INTO taxonomy_dag
SELECT gc.id, gc.article, gc.grounded, 0, ARRAY[gc.id], ARRAY[gc.id], NULL
FROM grounded_categories gc
WHERE
gc.broader = 'Category:Main_topic_classifications'
AND gc.grounded = 't'
AND gc.id NOT IN (
    'Category:Life',
    'Category:People',
    'Category:Chronology',
    'Category:Mathematics',
    'Category:Applied_sciences'
);

-- TODO remove applied sciences, mathematics and chronology from roots?


