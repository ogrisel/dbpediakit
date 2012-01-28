-- Arrays of array aggregation for materialized path management
-- Source: http://stackoverflow.com/questions/6643305/postgresql-select-array

-- define functions: array2_agg_cutfirst, array2_agg

CREATE OR REPLACE FUNCTION array2_agg_cutfirst(res anyarray)
RETURNS anyarray AS $$ 
BEGIN
    RETURN res[2:array_length(res, 1)];
END $$
LANGUAGE 'plpgsql';

CREATE AGGREGATE array2_agg(anyarray)
(
    SFUNC = array_cat,
    STYPE = anyarray,
    FINALFUNC = array2_agg_cutfirst,
    INITCOND = '{{0, 0}}'
);

