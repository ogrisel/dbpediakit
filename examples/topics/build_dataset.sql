-- Collect examples for each grounded topic of the taxonmy to train a text
-- classification model

-- Author: Olivier Grisel
-- License: MIT

-- define tables: taxonomy_articles, grouped_taxonomy_articles

DROP TABLE IF EXISTS taxonomy_articles;
CREATE TABLE taxonomy_articles (
    id varchar(300),
    grounded_topic varchar(300)
);

-- insert articles that are directly categorized with a grounded topic
INSERT INTO taxonomy_articles
SELECT ac.source, td.id
FROM
  (SELECT DISTINCT id FROM taxonomy_dag WHERE grounded = 'f') AS td,
  article_categories ac
WHERE td.id = ac.target;

-- insert articles that have indirect categorization by narrower non
-- grounded categories
INSERT INTO taxonomy_articles
SELECT ac.source, grounded.id
FROM
  (SELECT DISTINCT id FROM taxonomy_dag WHERE grounded = 't') AS grounded,
  (SELECT id, broader FROM grounded_categories WHERE grounded = 'f') AS nongrounded,
  article_categories ac
WHERE
  grounded.id = nongrounded.broader
  AND nongrounded.id = ac.target;


-- Group categories ids to ease the final extraction
DROP TABLE IF EXISTS grouped_taxonomy_articles;
CREATE TABLE grouped_taxonomy_articles (
    id varchar(300),
    grounded_topics varchar(300)[]
);

INSERT INTO grouped_taxonomy_articles
SELECT ta.id, array_agg(ta.grounded_topic)
FROM (SELECT DISTINCT * FROM taxonomy_articles) AS ta
GROUP BY ta.id;
