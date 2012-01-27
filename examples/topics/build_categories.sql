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

-- Descend the broader to narrower relationship from handpicked grounded
-- roots

-- TODO
