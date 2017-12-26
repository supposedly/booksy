#encoding: utf-8
permissions = [
  'manage location',
  'manage accounts',
  'manage roles',
  'create administrative roles',
  'manage media',
  'generate reports',
  ]
maximums = [
  'max renewals',
  'max checkouts',
  'max checkout duration',
  ]
acct_locks = [
  'max fines',
  'max checkouts',
  ]

async def create_pg_tables(conn):
    query = """
    CREATE TABLE IF NOT EXISTS
      locations (
        lid BIGSERIAL PRIMARY KEY,
        name TEXT,
        ip TEXT UNIQUE,
        fine_amt NUMERIC DEFAULT 0.10,
        fine_interval INT DEFAULT 1
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
        acquired TIMESTAMP
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
        );
    """
    await conn.execute(query)
