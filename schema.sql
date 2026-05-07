CREATE DATABASE IF NOT EXISTS final_project;
USE final_project;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS paperresearchfundingagencies;
DROP TABLE IF EXISTS paperlanguages;
DROP TABLE IF EXISTS papercountries;
DROP TABLE IF EXISTS countries;
DROP TABLE IF EXISTS papercontinents;
DROP TABLE IF EXISTS continents;
DROP TABLE IF EXISTS paperauthorinstitutions;
DROP TABLE IF EXISTS institutions;
DROP TABLE IF EXISTS paperauthors;
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

CREATE TABLE paperauthors (
  paper_author_id INT AUTO_INCREMENT PRIMARY KEY,
  paper_id INT NOT NULL,
  author_position INT NOT NULL,
  author_name VARCHAR(255) NOT NULL,
  UNIQUE KEY uniq_paper_author_position (paper_id, author_position),
  CONSTRAINT fk_paperauthors_paper
    FOREIGN KEY (paper_id) REFERENCES papers (paper_id)
);

CREATE TABLE institutions (
  institution_id INT AUTO_INCREMENT PRIMARY KEY,
  institution_name VARCHAR(512) NOT NULL,
  UNIQUE KEY uniq_institution_name (institution_name)
);

CREATE TABLE paperauthorinstitutions (
  paper_author_id INT NOT NULL,
  institution_position INT NOT NULL,
  institution_id INT NULL,
  author_country VARCHAR(128),
  PRIMARY KEY (paper_author_id, institution_position),
  CONSTRAINT fk_paperauthorinstitutions_author
    FOREIGN KEY (paper_author_id) REFERENCES paperauthors (paper_author_id),
  CONSTRAINT fk_paperauthorinstitutions_institution
    FOREIGN KEY (institution_id) REFERENCES institutions (institution_id)
);

CREATE TABLE continents (
  continent_id INT AUTO_INCREMENT PRIMARY KEY,
  continent_name VARCHAR(128) NOT NULL,
  UNIQUE KEY uniq_continent_name (continent_name)
);

CREATE TABLE papercontinents (
  paper_continent_id INT AUTO_INCREMENT PRIMARY KEY,
  paper_id INT NOT NULL,
  continent_position INT NOT NULL,
  continent_id INT NOT NULL,
  UNIQUE KEY uniq_paper_continent_position (paper_id, continent_position),
  CONSTRAINT fk_papercontinents_paper
    FOREIGN KEY (paper_id) REFERENCES papers (paper_id),
  CONSTRAINT fk_papercontinents_continent
    FOREIGN KEY (continent_id) REFERENCES continents (continent_id)
);

CREATE TABLE countries (
  country_id INT AUTO_INCREMENT PRIMARY KEY,
  country_name VARCHAR(128) NOT NULL,
  UNIQUE KEY uniq_country_name (country_name)
);

CREATE TABLE papercountries (
  paper_continent_id INT NOT NULL,
  country_position INT NOT NULL,
  country_id INT NOT NULL,
  fcv_status VARCHAR(32),
  income_level VARCHAR(64),
  PRIMARY KEY (paper_continent_id, country_position),
  CONSTRAINT fk_papercountries_papercontinent
    FOREIGN KEY (paper_continent_id) REFERENCES papercontinents (paper_continent_id),
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
