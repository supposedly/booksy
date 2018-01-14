CREATE TABLE IF NOT EXISTS
  locations (
    lid BIGSERIAL PRIMARY KEY,
    name TEXT,
    ip TEXT UNIQUE,
    fine_amt NUMERIC DEFAULT 0.10,
    fine_interval INT DEFAULT 1,
    media_types TEXT[] DEFAULT '{book, other}',
    color SMALLINT,
    image BYTEA
  );
CREATE TABLE IF NOT EXISTS 
  members (
    uid BIGSERIAL PRIMARY KEY,
    username TEXT,
    lid BIGINT,
    UNIQUE(username, lid),
    fullname TEXT,
    email TEXT,
    phone TEXT,
    manages BOOL DEFAULT false,
    rid BIGINT,
    checkouts BIGINT,
    pwhash bytea,
    type SMALLINT,
    perms BIGINT,
    maxes BIGINT,
    locks BIGINT
  );
CREATE TABLE IF NOT EXISTS
  items (
    mid BIGSERIAL UNIQUE PRIMARY KEY,
    type TEXT,
    isbn TEXT,
    lid BIGINT,
    title TEXT,
    author TEXT,
    published DATE,
    genre TEXT,
    issued_to BIGINT,
    due_date DATE,
    fines NUMERIC,
    acquired TIMESTAMP,
    maxes BIGINT
  );
CREATE TABLE IF NOT EXISTS
  holds (
    mid BIGINT,
    uid BIGINT,
    created TIMESTAMP,
    PRIMARY KEY(mid, uid)
  );
CREATE TABLE IF NOT EXISTS
  roles (
    rid BIGSERIAL UNIQUE PRIMARY KEY,
    lid BIGINT,
    name TEXT,
    permissions SMALLINT,
    maxes BIGINT,
    locks BIGINT
  );

-- -- -- -- -- -- -- -- -- -- -- -- -- -- --

CREATE TABLE IF NOT EXISTS
  help (
    id BIGSERIAL PRIMARY KEY,
    title TEXT,
    content TEXT
  );
