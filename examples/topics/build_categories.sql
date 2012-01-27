-- Script to materialized a sensible enough taxonomy from the Wikipedia
-- categories tree

-- Author: Olivier Grisel <olivier.grisel@ensta.org>
-- License: MIT

-- Expand the redirects

DROP TABLE IF EXISTS redirected_categories;
CREATE TABLE redirected_categories (
    id varchar(300),
    broader varchar(300),
    candidate_article varchar(300)
);

INSERT INTO redirected_categories
SELECT c.id, c.broader,
CASE WHEN (r.target IS NULL) THEN c.candidate_article
ELSE r.target
  END AS candidate_article
FROM categories c
LEFT OUTER JOIN redirects r
ON c.candidate_article = r.source;

-- Materialize the interesting categories by looking up those with a matching
-- wikipedia article with a not so short abstract

DROP TABLE IF EXISTS semantic_categories;
CREATE TABLE semantic_categories (
    id varchar(300),
    broader varchar(300),
    semantic bool,
    article varchar(300)
);

INSERT INTO semantic_categories
SELECT c.id, c.broader,
a.text IS NOT NULL AS semantic,
CASE WHEN (a.text IS NOT NULL) THEN a.id
ELSE NULL
  END AS article
FROM redirected_categories c
LEFT OUTER JOIN long_abstracts a
ON c.candidate_article = a.id;

CREATE INDEX semantic_categories_id_idx ON semantic_categories (id);
CREATE INDEX semantic_categories_broader_idx ON semantic_categories (broader);
CREATE INDEX semantic_categories_article_idx ON semantic_categories (article);

-- Descend the broader to narrower relationship from handpicked semantic
-- roots

-- TODO
