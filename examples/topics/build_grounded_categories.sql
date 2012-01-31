-- Script to find categories that have a matching Wikipedia article
-- We call those categories "grounded categories" or "grounded topics" when
-- part of a taxonomy

-- Author: Olivier Grisel <olivier.grisel@ensta.org>
-- License: MIT

-- define tables: redirected_categories, grounded_categories

-- Ignore broader links and follow the redirects if any

DROP TABLE IF EXISTS redirected_categories;
CREATE TABLE redirected_categories (
    id varchar(300),
    broader varchar(300),
    candidate_article varchar(300)
);

INSERT INTO redirected_categories
SELECT DISTINCT c.id, c.broader,
CASE WHEN (r.target IS NULL) THEN c.candidate_article
ELSE r.target
  END AS candidate_article
FROM categories c
LEFT OUTER JOIN redirects r
ON c.candidate_article = r.source;

-- Materialize the interesting categories by looking up those with a matching
-- wikipedia article with a not so short abstract: we name this subset as
-- "semantically grounded": they have a matching real life concept.

DROP TABLE IF EXISTS grounded_categories;
CREATE TABLE grounded_categories (
    id varchar(300),
    broader varchar(300),
    grounded bool,
    article varchar(300)
);

INSERT INTO grounded_categories
SELECT c.id, c.broader,
a.text IS NOT NULL AS grounded,
CASE WHEN (a.text IS NOT NULL) THEN a.id
ELSE NULL
  END AS article
FROM redirected_categories c
LEFT OUTER JOIN long_abstracts a
ON c.candidate_article = a.id;

CREATE INDEX grounded_categories_id_idx ON grounded_categories (id);
CREATE INDEX grounded_categories_broader_idx ON grounded_categories (broader);
CREATE INDEX grounded_categories_article_idx ON grounded_categories (article);
