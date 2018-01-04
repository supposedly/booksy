INSERT INTO locations (
              name, ip,
              color, image
            )
     SELECT $1::text, $2::text,
            $2::smallint, $3::bytea;

-- ROLES SETUP --

INSERT INTO roles (
              lid, name,
              permissions, 
              maxes, locks
              )
     SELECT currval(pg_get_serial_sequence('locations', 'lid')),
            'Admin'::text,
            32767::smallint, -- maximum smallint value, so every permission bc admin
            9223372036854775807::bigint, -- maximum bigint value, so no maxes
            9223372036854775807::bigint; -- maximum bigint value, so no locks

INSERT INTO roles (
              lid, name, 
              permissions, 
              maxes, locks
              )
     SELECT currval(pg_get_serial_sequence('locations', 'lid')),
            'Organizer'::text,
            55::smallint, -- 0110111
            1028::bigint, -- 4, 4, 0...
            5140::bigint; -- 20, 20, 0 . . .

INSERT INTO roles (
              lid, name, 
              permissions, 
              maxes, locks
              )
     SELECT currval(pg_get_serial_sequence('locations', 'lid')),
            'Subscriber'::text,
            0::smallint, -- 0000000
            514::bigint, -- 2, 2, 0 . . .
            5135::bigint; -- 15, 15, 0 . . .

-- END ROLES SETUP --

-- ACCOUNTS SETUP --

INSERT INTO members (
              username, pwhash,
              lid, rid,
              fullname,
              manages, type
              )
     SELECT $4::text, $5::bytea, -- checkout acct; username determined by backend (usually school initials plus '-checkout-XX' [unique digits])
            currval(pg_get_serial_sequence('locations', 'lid')),
            currval(pg_get_serial_sequence('roles', 'rid')),
            locations.name + ' Patron',
            false, 1
       FROM locations
      WHERE lid = currval(pg_get_serial_sequence('locations', 'lid'));

INSERT INTO members (
              username, pwhash,
              lid, rid,
              fullname, email, phone,
              manages, type
              )
     SELECT $6::text, $7::bytea, -- admin acct; username determined by backend (usually school initials + '-admin')
            currval(pg_get_serial_sequence('locations', 'lid')),
            currval(pg_get_serial_sequence('roles', 'rid')),
            $8::text, $9::text, $10::text,
            true, 0;

-- END ACCOUNTS SETUP --

SELECT currval(pg_get_serial_sequence('locations', 'lid'))
