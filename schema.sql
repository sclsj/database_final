CREATE DATABASE IF NOT EXISTS final_project;
USE final_project;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS paperresearchfundingagencies;
DROP TABLE IF EXISTS paperlanguages;
DROP TABLE IF EXISTS papercountries;
DROP TABLE IF EXISTS papercontinents;
DROP TABLE IF EXISTS paperauthors;
DROP TABLE IF EXISTS authors;
DROP TABLE IF EXISTS countries;
DROP TABLE IF EXISTS continents;
DROP TABLE IF EXISTS languages;
DROP TABLE IF EXISTS agencies;
DROP TABLE IF EXISTS papers;

SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE papers (
  paper_id INT PRIMARY KEY,
  product_type VARCHAR(16),
  title TEXT,
  year_of_publication INT,
  sector_name VARCHAR(128),
  abstract TEXT,
  evaluation_design VARCHAR(64),
  evaluation_method VARCHAR(128)
);

CREATE TABLE agencies (
  agency_id INT AUTO_INCREMENT PRIMARY KEY,
  agency_name VARCHAR(512) NOT NULL,
  UNIQUE KEY uniq_agency_name (agency_name)
);

CREATE TABLE authors (
  author_id INT AUTO_INCREMENT PRIMARY KEY,
  author_name VARCHAR(255) NOT NULL,
  agency_id INT NULL,
  author_country VARCHAR(128),
  UNIQUE KEY uniq_author_name (author_name),
  CONSTRAINT fk_authors_agency
    FOREIGN KEY (agency_id) REFERENCES agencies (agency_id)
);

CREATE TABLE paperauthors (
  paper_id INT NOT NULL,
  author_position INT NOT NULL,
  author_id INT NOT NULL,
  PRIMARY KEY (paper_id, author_position),
  CONSTRAINT fk_paperauthors_paper
    FOREIGN KEY (paper_id) REFERENCES papers (paper_id),
  CONSTRAINT fk_paperauthors_author
    FOREIGN KEY (author_id) REFERENCES authors (author_id)
);

CREATE TABLE continents (
  continent_id INT AUTO_INCREMENT PRIMARY KEY,
  continent_name VARCHAR(128) NOT NULL,
  UNIQUE KEY uniq_continent_name (continent_name)
);

CREATE TABLE papercontinents (
  paper_id INT NOT NULL,
  continent_id INT NOT NULL,
  PRIMARY KEY (paper_id, continent_id),
  CONSTRAINT fk_papercontinents_paper
    FOREIGN KEY (paper_id) REFERENCES papers (paper_id),
  CONSTRAINT fk_papercontinents_continent
    FOREIGN KEY (continent_id) REFERENCES continents (continent_id)
);

CREATE TABLE countries (
  country_id INT AUTO_INCREMENT PRIMARY KEY,
  country_name VARCHAR(128) NOT NULL,
  continent_id INT NULL,
  fcv_status VARCHAR(32),
  income_level VARCHAR(64),
  UNIQUE KEY uniq_country_name (country_name),
  CONSTRAINT fk_countries_continent
    FOREIGN KEY (continent_id) REFERENCES continents (continent_id)
);

CREATE TABLE papercountries (
  paper_id INT NOT NULL,
  country_id INT NOT NULL,
  PRIMARY KEY (paper_id, country_id),
  CONSTRAINT fk_papercountries_paper
    FOREIGN KEY (paper_id) REFERENCES papers (paper_id),
  CONSTRAINT fk_papercountries_country
    FOREIGN KEY (country_id) REFERENCES countries (country_id)
);

CREATE TABLE languages (
  language_id INT AUTO_INCREMENT PRIMARY KEY,
  language_name VARCHAR(64) NOT NULL,
  UNIQUE KEY uniq_language_name (language_name)
);

CREATE TABLE paperlanguages (
  paper_id INT NOT NULL,
  language_id INT NOT NULL,
  PRIMARY KEY (paper_id, language_id),
  CONSTRAINT fk_paperlanguages_paper
    FOREIGN KEY (paper_id) REFERENCES papers (paper_id),
  CONSTRAINT fk_paperlanguages_language
    FOREIGN KEY (language_id) REFERENCES languages (language_id)
);

CREATE TABLE paperresearchfundingagencies (
  paper_id INT NOT NULL,
  agency_id INT NOT NULL,
  PRIMARY KEY (paper_id, agency_id),
  CONSTRAINT fk_paperfunders_paper
    FOREIGN KEY (paper_id) REFERENCES papers (paper_id),
  CONSTRAINT fk_paperfunders_agency
    FOREIGN KEY (agency_id) REFERENCES agencies (agency_id)
);
