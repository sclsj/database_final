USE final_project;

-- most paper-published year

SELECT year_of_publication, COUNT(*) as paper_num
FROM papers WHERE year_of_publication IS NOT NULL
GROUP BY year_of_publication 
ORDER BY paper_num DESC;

-- top 10 authors with most publications

SELECT author_name, COUNT(DISTINCT paper_id)
as paper_num FROM authors WHERE author_name
IS NOT NULL AND author_name != '' GROUP BY author_name
ORDER BY paper_num DESC LIMIT 10;

-- Top 10 studied countries

SELECT country_name, COUNT(DISTINCT paper_id) as paper_num
FROM countries WHERE country_name IS NOT NULL AND
country_name != ''
GROUP BY country_name ORDER BY paper_num DESC
LIMIT 10;