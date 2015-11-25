-- Celebrity news database structure


CREATE TABLE IF NOT EXISTS sources
-- Plenty of news sites are there*/
(
	id serial PRIMARY KEY,
	s_name text UNIQUE,
	s_url text UNIQUE
);


CREATE TABLE IF NOT EXISTS news 
-- News in a terse mode
(
	id serial PRIMARY KEY,
	source_id integer,
	headline text,
	summary text,
	url text,
	img_url text,
	keywords text[],
	CONSTRAINT fk_so FOREIGN KEY (source_id)
		   REFERENCES sources (id)
		   ON UPDATE CASCADE
		   ON DELETE CASCADE
);
