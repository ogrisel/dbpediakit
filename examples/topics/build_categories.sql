-- Script to materialized a sensible enough taxonomy from the Wikipedia
-- categories tree

-- Author: Olivier Grisel <olivier.grisel@ensta.org>
-- License: MIT

-- Materialize the interesting categories by looking up those with a matching
-- wikipedia article with a not so short abstract

-- CREATE TABLE semantic_categories (
--     id varchar(300),
--     broader varchar(300),
--     semantic bool,
--     article varchar(300)
-- );
-- 
-- INSERT INTO semantic_categories
-- SELECT c.id, c.broader,
-- a.text IS NOT NULL AS semantic,
-- CASE WHEN (a.text IS NOT NULL) THEN a.id
-- ELSE NULL
--   END AS article
-- FROM categories c LEFT OUTER JOIN long_abstracts a
-- ON c.candidate_article = a.id;

CREATE INDEX semantic_categories_id_idx ON semantic_categories (id);
CREATE INDEX semantic_categories_broader_idx ON semantic_categories (broader);
CREATE INDEX semantic_categories_article_idx ON semantic_categories (article);

-- Descend the broader to narrower relationship from handpicked semantic
-- roots

-- TODO
