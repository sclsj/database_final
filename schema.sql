CREATE DATABASE IF NOT EXISTS final_project;
USE final_project;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS recordresearchfundingagencies;
DROP TABLE IF EXISTS recordlanguages;
DROP TABLE IF EXISTS recordcountries;
DROP TABLE IF EXISTS countries;
DROP TABLE IF EXISTS recordcontinents;
DROP TABLE IF EXISTS continents;
DROP TABLE IF EXISTS recordauthorinstitutions;
DROP TABLE IF EXISTS institutions;
DROP TABLE IF EXISTS recordauthors;
DROP TABLE IF EXISTS languages;
DROP TABLE IF EXISTS agencies;
DROP TABLE IF EXISTS records;

SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE records (
  record_id INT PRIMARY KEY,
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

CREATE TABLE recordauthors (
  record_author_id INT AUTO_INCREMENT PRIMARY KEY,
  record_id INT NOT NULL,
  author_position INT NOT NULL,
  author_name VARCHAR(255) NOT NULL,
  UNIQUE KEY uniq_record_author_position (record_id, author_position),
  CONSTRAINT fk_recordauthors_record
    FOREIGN KEY (record_id) REFERENCES records (record_id)
);

CREATE TABLE institutions (
  institution_id INT AUTO_INCREMENT PRIMARY KEY,
  institution_name VARCHAR(512) NOT NULL,
  UNIQUE KEY uniq_institution_name (institution_name)
);

CREATE TABLE recordauthorinstitutions (
  record_author_id INT NOT NULL,
  institution_position INT NOT NULL,
  institution_id INT NULL,
  institution_country VARCHAR(128),
  PRIMARY KEY (record_author_id, institution_position),
  CONSTRAINT fk_recordauthorinstitutions_author
    FOREIGN KEY (record_author_id) REFERENCES recordauthors (record_author_id),
  CONSTRAINT fk_recordauthorinstitutions_institution
    FOREIGN KEY (institution_id) REFERENCES institutions (institution_id)
);

CREATE TABLE continents (
  continent_id INT AUTO_INCREMENT PRIMARY KEY,
  continent_name VARCHAR(128) NOT NULL,
  UNIQUE KEY uniq_continent_name (continent_name)
);

CREATE TABLE recordcontinents (
  record_continent_id INT AUTO_INCREMENT PRIMARY KEY,
  record_id INT NOT NULL,
  record_continent_position INT NOT NULL,
  continent_id INT NOT NULL,
  UNIQUE KEY uniq_record_continent_position (record_id, record_continent_position),
  CONSTRAINT fk_recordcontinents_record
    FOREIGN KEY (record_id) REFERENCES records (record_id),
  CONSTRAINT fk_recordcontinents_continent
    FOREIGN KEY (continent_id) REFERENCES continents (continent_id)
);

CREATE TABLE countries (
  country_id INT AUTO_INCREMENT PRIMARY KEY,
  country_name VARCHAR(128) NOT NULL,
  UNIQUE KEY uniq_country_name (country_name)
);

CREATE TABLE recordcountries (
  record_country_id INT AUTO_INCREMENT PRIMARY KEY,
  record_continent_id INT NOT NULL,
  record_country_position INT NOT NULL,
  country_id INT NOT NULL,
  fcv_status VARCHAR(32),
  income_level VARCHAR(64),
  UNIQUE KEY uniq_record_country_position (record_continent_id, record_country_position),
  CONSTRAINT fk_recordcountries_recordcontinent
    FOREIGN KEY (record_continent_id) REFERENCES recordcontinents (record_continent_id),
  CONSTRAINT fk_recordcountries_country
    FOREIGN KEY (country_id) REFERENCES countries (country_id)
);

CREATE TABLE languages (
  language_id INT AUTO_INCREMENT PRIMARY KEY,
  language_name VARCHAR(64) NOT NULL,
  UNIQUE KEY uniq_language_name (language_name)
);

CREATE TABLE recordlanguages (
  record_id INT NOT NULL,
  language_id INT NOT NULL,
  PRIMARY KEY (record_id, language_id),
  CONSTRAINT fk_recordlanguages_record
    FOREIGN KEY (record_id) REFERENCES records (record_id),
  CONSTRAINT fk_recordlanguages_language
    FOREIGN KEY (language_id) REFERENCES languages (language_id)
);

CREATE TABLE recordresearchfundingagencies (
  record_id INT NOT NULL,
  agency_id INT NOT NULL,
  PRIMARY KEY (record_id, agency_id),
  CONSTRAINT fk_recordfunders_record
    FOREIGN KEY (record_id) REFERENCES records (record_id),
  CONSTRAINT fk_recordfunders_agency
    FOREIGN KEY (agency_id) REFERENCES agencies (agency_id)
);
