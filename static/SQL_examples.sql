-- SCHEMA SETUP --
CREATE TABLE IF NOT EXISTS
  locations (
    lid BIGSERIAL PRIMARY KEY,
    name TEXT,
    ip TEXT UNIQUE,
    fine_amt NUMERIC DEFAULT 0.10,
    fine_interval INT DEFAULT 1,
    media_types TEXT[] DEFAULT '{book, other}'
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
    manages BOOL,
    rid BIGINT,
    checkouts BIGINT,
    pwhash TEXT,
    type SMALLINT
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
-- END SCHEMA SETUP --
-- SAMPLE LIBRARY REGISTRATION --
INSERT INTO locations (name, ip)
     SELECT 'East High School',
            '192.168.1.1';

INSERT INTO roles (
              lid, name,
              permissions, 
              maxes, locks
              )
     SELECT currval(pg_get_serial_sequence('locations', 'lid')),
            'Admin',
            32767, -- maximum smallint value, so every permission bc admin
            9223372036854775807, -- maximum bigint value, so no maxes
            9223372036854775807; -- maximum bigint value, so no locks

INSERT INTO roles (
              lid, name, 
              permissions, 
              maxes, locks
              )
     SELECT currval(pg_get_serial_sequence('locations', 'lid')),
            'Organizer',
            55, -- 0110111
            9223372036854775807, -- maximum bigint value, so no maxes
            9223372036854775807; -- maximum bigint value, so no locks

INSERT INTO members (
              username, pwhash,
              lid, rid,
              fullname, email, phone,
              manages, type
              )
     SELECT 'eh-checkout-00', 'SOMEHASH',
            currval(pg_get_serial_sequence('locations', 'lid')),
            currval(pg_get_serial_sequence('roles', 'rid')),
            'East High School Patron',
            NULL, NULL,
            false, 1;

INSERT INTO members (
              username, pwhash,
              lid, rid,
              fullname, email, phone,
              manages, type
              )
     SELECT 'eh-admin', 'h45hbr0wn5!!!1',
            currval(pg_get_serial_sequence('locations', 'lid')),
            currval(pg_get_serial_sequence('roles', 'rid')),
            'John Cena',
            'jhcena@gmail.com',
            '4254225309',
            true, 0;
INSERT INTO items (
              type, genre,
              isbn, lid, 
              title, author, published, 
              issued_to, due_date, fines,
              acquired
              )
     SELECT 'book', 'fantasy',
            NULL,
            currval(pg_get_serial_sequence('locations', 'lid')), -- in prod this will be provided as parameter
            'Harry Potter and the Blithering Whatever',
            'JK Rowling',
            '12-13-14'::date,
            NULL, NULL, NULL,
            current_date;
-- END SAMPLE LIBRARY REGISTRATION --
-- SAMPLE MEDIA CHECKOUT --
UPDATE items
   SET issued_to = ($2), -- given as param
       due_date = current_date + ($3), -- time-allowed parameter calculated in python bc would be awful in plpgsql
       fines = 0
 WHERE mid = ($1);
 -- END SAMPLE MEDIA CHECKOUT --

