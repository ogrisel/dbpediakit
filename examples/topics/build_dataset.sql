-- Collect examples for each grounded topic of the taxonmy to train a text
-- classification model

-- Author: Olivier Grisel
-- License: MIT

-- define tables: taxonomy_examples

DROP TABLE IF EXISTS taxonomy_articles;
CREATE TABLE taxonomy_articles (
    id varchar(300),
    grounded_topic varchar(300)
);

-- insert articles that are directly categorized with a grounded topic
INSERT INTO taxonomy_articles
SELECT ac.source, td.id
FROM (SELECT DISTINCT id, grounded FROM taxonomy_dag) AS td, article_categories ac
WHERE td.id = ac.target AND td.grounded = 't';
