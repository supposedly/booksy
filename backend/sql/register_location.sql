INSERT INTO locations (
              name, ip, color --, image
            )
     SELECT $1::text, $2::text,
            $3::smallint; --, NULL -- for image

-- ROLES SETUP --

INSERT INTO roles (
              lid, name,
              isdefault,
              permissions, 
              maxes, locks
              )
     SELECT currval(pg_get_serial_sequence('locations', 'lid')),
            'Admin'::text,
            TRUE,
            127::smallint, -- 32767::smallint, -- maximum smallint value, so every permission bc admin
            -1::bigint, -- 9223372036854775807::bigint, -- maximum bigint value, so no maxes
            -1::bigint; -- 9223372036854775807::bigint[semicolon] -- maximum bigint value, so no locks

INSERT INTO roles (
              lid, name,
              isdefault,
              permissions, 
              maxes, locks
              )
     SELECT currval(pg_get_serial_sequence('locations', 'lid')),
            'Organizer'::text,
            TRUE,
            55::smallint, -- 0110111
            1028::bigint, -- 4, 4, 0...
            5140::bigint; -- 20, 20, 0 . . .

INSERT INTO roles (
              lid, name,
              isdefault,
              permissions, 
              maxes, locks
              )
     SELECT currval(pg_get_serial_sequence('locations', 'lid')),
            'Subscriber'::text,
            TRUE,
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
     SELECT $1::text, $2::bytea, -- checkout acct -- username determined by backend (usually school initials plus '-checkout-XX' [unique digits])
            currval(pg_get_serial_sequence('locations', 'lid')),
            currval(pg_get_serial_sequence('roles', 'rid')),
            locations.name || ' Patron',
            false, 1
       FROM locations
      WHERE lid = currval(pg_get_serial_sequence('locations', 'lid'));

INSERT INTO members (
              username, pwhash,
              lid, rid,
              fullname, email, phone,
              manages, type
              )
     SELECT $1::text, $2::bytea, -- admin acct -- username determined by backend (usually school initials + '-admin')
            currval(pg_get_serial_sequence('locations', 'lid')),
            currval(pg_get_serial_sequence('roles', 'rid')),
            $3::text, $4::text, $5::text,
            true, 0;

-- END ACCOUNTS SETUP --

SELECT currval(pg_get_serial_sequence('locations', 'lid'));
