``Documentation and design specification`` for booksy.db

__[DESIGN SPEC]__
![!][NOTE:] Various UI and UX info goes here!
> Indeed it does.

__[CONCEPTS]__
![!][NOTE:] These are the abstract ideas and terms utilized in the rest of the documentation.
![!][CONT:] Skip to [LOGIN] for the start of the program-flow explication.
### [GLOSSARY] OF TERMS ###
   > User:
      Any person utilizing the application, regardless of what they do with it.
   > Chieftain:
      Blanket term for a user allowed some degree of administrative freedom.
      This applies by default to the Administrator and Organizer roles.
   > Member, user:
      Anyone registered in the database as a library patron.
   > Administrator, Organizer, Subscriber:
      The three roles present by default. See [ROLES] for more explanation.
   > Media:
      Anything the library may offer to members, as defined by the location's
      administrator(s). By default, this is limited to "book".
   > Item:
      Any single piece of media.
   > Location, library:
      Interchangeable terms used to refer to a public institution that utilizes
      this application to manage media distribution.
### [ROLES] ###
   >> Roles are permission groups assigned to users that determine the degree of freedom
      to which these users are allowed to use the application. There are three default
      roles, described below.
   ----
   > Administrator:
      The top-dog of the role hierarchy.
      These users are able to manage the location's info (name, picture, color scheme, etc)
      and to create roles with the ability to create other roles. They also have all the
      permissions given to lower roles, sans managing users' accounts (besides deletion).
      This role is assigned by default to a location
   > Organizer:
      Users with permission to manage members and add new media to the database. This is
      assigned 
   > Subscriber:
      Users with just the ability to manage their own account and check out media.
### THE [DATABASE] ###
   >> Everything to do with libraries and their status will be stored in a
      postgreSQL database (the same DB provisioned by Heroku to its users).
      This database will contain five tables; the primary keys `lid, mid, rid, uid` represent
      respectively Location ID, Media ID, Role ID, and User ID. User is synonymous here with
      member. The tables are described below:
   ----
   > locations:
      Every single library currently registered with Booksy, with record of their
      IP address and/or subnet (whichever applicable).
         ╔══════════════════════╦═══════════╦══════╦══════════════════╦═══════════╗
         ║ lid (PRIMARY KEY)    ║ name      ║ ip   ║ username         ║ pwhash    ║
         ╠══════════════════════╬═══════════╬══════╬══════════════════╬═══════════╣
         ║ BIGINT               ║ TEXT      ║ TEXT ║ TEXT             ║ TEXT      ║
         ║ (unique location ID) ║ (location ║      ║ (self-checkout   ║ (bcrypted ║
         ║                      ║ name)     ║      ║ acct's username) ║ password) ║
         ╚══════════════════════╩═══════════╩══════╩══════════════════╩═══════════╝
   > members:
      Data for every single patron across libraries.
         ╔════════════════════╦══════════╦═════════════╦══════════╦══════════╦════════════╦══════════════════╦════════════════╦═══════════╦════════════╗
         ║ uid (PRIMARY KEY)  ║ username ║ fullname    ║ email    ║ phone    ║ lid        ║ manages          ║ rid            ║ pwhash    ║ extra      ║
         ╠════════════════════╬══════════╬═════════════╬══════════╬══════════╬════════════╬══════════════════╬════════════════╬═══════════╬════════════╣
         ║ BIGINT             ║ TEXT     ║ TEXT        ║ TEXT     ║ TEXT     ║ BIGINT     ║ BOOL             ║ BIGINT         ║ TEXT      ║ TEXT       ║
         ║ (unique member ID) ║          ║ (full name) ║ (email   ║ (phone # ║ (location) ║ (can they manage ║ (ID of this    ║ (bcrypted ║ (anything) ║
         ║                    ║          ║             ║ or null) ║ or null) ║            ║ this location?)  ║ member's role) ║ password) ║            ║
         ╚════════════════════╩══════════╩═════════════╩══════════╩══════════╩════════════╩══════════════════╩════════════════╩═══════════╩════════════╝
   > items:
      Every single item in every registered library, with records of their
      location and checkout data if applicable (else NULL).
         ╔═══════════════════════╦════════════╦════════════════════╦══════════════╦═══════╦════════╦═══════════╦══════════════╦════════════╦════════════╦═════════════════╦════════════╗
         ║ mid (PRIMARY KEY)     ║ type       ║ isbn               ║ lid          ║ title ║ author ║ published ║ issuedto     ║ due        ║ fines      ║ acquired        ║ extra      ║
         ╠═══════════════════════╬════════════╬════════════════════╬══════════════╬═══════╬════════╬═══════════╬══════════════╬════════════╬════════════╬═════════════════╬════════════╣
         ║ BIGINT                ║ TEXT       ║ TEXT               ║ BIGINT       ║ TEXT  ║ TEXT   ║ DATE      ║ BIGINT       ║ TIMESTAMP  ║ MONEY      ║ TIMESTAMP       ║ TEXT       ║
         ║ (internal ID of item) ║ ('book' or ║ (maybe bigint)     ║ (internal id ║       ║        ║           ║ (user ID, or ║ (when this ║ (overdue   ║ (when this copy ║ (anything) ║
         ║                       ║ whatever)  ║ (null if not book) ║ of location) ║       ║        ║           ║ NULL if not  ║ should be  ║ fines on   ║ was added to    ║            ║
         ║                       ║            ║                    ║              ║       ║        ║           ║ checked out) ║ returned)  ║ this item) ║ the location)   ║            ║
         ╚═══════════════════════╩════════════╩════════════════════╩══════════════╩═══════╩════════╩═══════════╩══════════════╩════════════╩════════════╩═════════════════╩════════════╝
   > holds:
      Holds on every item, with just the item's ID and ID of the user placing it on hold.
      Pairs form composite primary key.
         ╔═══════════╦═════════════╗
         ║ mid       ║ uid         ║
         ╠═══════════╬═════════════╣
         ║ BIGINT    ║ BIGINT      ║
         ║ (item id) ║ (member id) ║
         ╚═══════════╩═════════════╝
   > roles:
      Every role registered, with record of its perms and name.
      NOTE: Though not in the table yet, an lid BIGINT is also used.
         ╔═══════════════════╦═════════════╦════════════════╦═══════════════╦═══════════════╗
         ║ rid (PRIMARY KEY) ║ name        ║ permissions    ║ maxes         ║ locks         ║
         ╠═══════════════════╬═════════════╬════════════════╬═══════════════╬═══════════════╣
         ║ BIGINT            ║ TEXT        ║ SMALLINT       ║ BIGINT        ║ BIGINT        ║
         ║ (role ID)         ║ (role name) ║ (packed field; ║ (four 1-byte  ║ (two 1-byte   ║
         ║                   ║             ║ binary perms)  ║ numbers; more ║ numbers; more ║
         ║                   ║             ║                ║ reserved)     ║ reserved)     ║
         ╚═══════════════════╩═════════════╩════════════════╩═══════════════╩═══════════════╝
   >>The "permissions" packed field is as follows.
      1st bit: Manage location info
         Change things like the location's name, color scheme, and picture.
      2nd bit: Create & delete accounts
         Self-explanatory.
      3rd bit: Create & delete roles
         Self-explanatory.
      4th bit: Manage roles & permissions
         Change info relating to existing roles.
      5th bit: Manage media
         Add and remove books from the system as well as changing titles & metadata.
      *__Further bits are reserved for future use.__*
      __Ergo:__ A value of 22, binary [10111], in the first five bytes would mean that:
         This role can manage location info.
         This role cannot create & delete accounts.
         This role can create & delete other roles.
         This role can manage roles & permissions.
         This role can manage media.
   >>The "maxes" packed integer field is as follows.
     NOTE that a value of 255, binary [11111111], in any one byte field is interpreted
     as *infinity* -- i.e. no limit.
      1st byte: MAX RENEWALS
           The maximum amount of due-date renewals afforded to this role.
           Can also customize per media category.
      2nd byte: MAX CHECKOUTS
           The maximum amount of items this role may check out at a time.
           Can also customize per media category.
      3rd byte: CHECKOUT DURATION (WEEKS)
           The maximum amount of time this role may check out an item for.
           Can also customize per media category.
      *__Further bytes are reserved for future use.__*
      __Ergo:__ A value of 200449, binary [00000011 00001111 00000001], in
      the first three bytes would mean that:
         This role can renew media a maximum of 3 (00000011) times.
         This role can check out a maximum of 15 (00001111) items concurrently.
         This role can check out items for a maximum of 1 (00000010) weeks.
   >>The "locks" packed integer field is as follows. An account "lock", once instated, will
     remain active until the user reverses the circumstances that effected it. (This may
     mean returning a book, paying off a fine, re-verifying their account, ...)
     NOTE that all locks can be customized per-item as well, overriding any account locks
     provided here.
     NOTE again that a value of 255, binary [11111111], in any one byte field is interpreted
     as *infinity* -- i.e. no limit.
      1st byte: MAX FINES (USD)
         Maximum amount of USD in fines allowed before an account with
         this role is barred from checking out new media.
      2nd byte: MAX CHECKOUTS (USD)
         Maximum amount of items this role may check out before being
         barred from further borrowing of media.
      *__Further bytes are reserved for future use.__*
       __Ergo:__ A value of 
         
### [ACCOUNT CREATION] ###
   When accounts are created, 

__[LOGIN]__
> Users, if in a registered IP or subnet, will be presented with their
institution's chosen logo & colour scheme and a prompt to log in with
their credentials (usually consisting of an ID or username and a password).
   1. If the user does not have an account, they should request an
      administrator to follow [CONCEPTS][ACCOUNT CREATION] for them.
   2. If the user is not on a registered IP or IP subnet, they will still
      be given the option to log in - just with a generically-themed signup
      page. On entry and afterward, their user experience will be identical to that
      of somebody logging in from their library's Booksy page.
      (THIS IS THE OPTION GIVEN FOR THE FBLA DEMO)

**HOME**
![!][NOTE:] The following text makes a distinction between a *chieftain* and an *operator*.
![!][CONT:] See [CONCEPTS][GLOSSARY] and [CONCEPTS][ROLES] for more explanation.
![!][CONT:] In some cases, their duties will overlap. *Operator* in all contexts here can
![!][CONT:] be replaced by *chieftain*, but not always vice-versa.

> The "home page" tab is really a collection of pages, defaulting to [BOOK CHECKOUT] but with
other pages being shown in the sidebar. Depending on the user's permissions, certain sections
(indicated by the ![PERMISSIONS][X] line) may not be shown.
### [BOOK CHECKOUT] (default page) ###
   > ![PERMISSIONS][N/A]
   >> The checkout page, being likely the biggest reason anybody would want to use this
      application, will be redirected to immediately after login. Other pages, which
      will be expanded on below, are sectioned off to the sidebar.
   ----
   1. During checkout, members will firstly be requested to enter their
      unique ID or username in a field presented on the operator's screen.
         #) If the member is unable to produce an ID or username, a chieftain
            is able to look them up in the database by first and last name or
            by any other potentially-identifying traits.
            If the user cannot be found in the database, the chieftain can
            go through the process of creating an account for them.
   2. Subsequently, the operator will be able to scan or enter manually the
      unique ID of the requested media in yet another field on the checkout
      screen.
         #) If the requested media for whatever reason has no accessible
            barcode, then the operator is able to look it up in the
            database by title, author, or any other potentially-
            identifying traits.
         #) If the requested media cannot presently be found in the
            database BUT the user would like to donate it, then a
            chieftain has the ability to add it into the system; the web
            application will provide and store a newly-generated ID for
            it "on the spot".
               a. In doing so, the chieftain must provide its:
                     1. Title,
                     2. Author or creator's name,
                     3. Media type (from a dropdown), and
                     4. Date of publication (if applicable).
                  They can also provide a picture, although this will
                  probably not be feasible in a time-crunched scenario
                  and so is optional.
               b. The chieftain will then have the option of printing
                  out the newly-generated barcode, or writing it down,
                  or even just leaving it alone to be added to the book
                  later. (Last option is not recommended)
   3. When both fields are filled out and the "Enter" or "Submit" button
      is pressed, the media is sent to the server to be recorded in the
      database.
         #) If the media is already checked out and to the same member,
            the operator will have the choice of either returning or
            renewing it. Renew limits will be defined per role, but
            are able to be overriden on a per-item basis.
         #) If the user is unable to check out the book - say, because
            they have too many active books checked out or a large
            amount of overdue fines - the server will return an error
            to be displayed on the webpage, and the checkout will not
            be accepted.
         #) If the book is not found in the database, another error
            will be returned, with the option to retype the ID or
            add the book to the database.
   4. User ID will persist for subsequent checkouts in the same session.

### [MY ACCOUNT] ###
   > ![PERMISSIONS][N/A]
   >> This page facilitates the modification of account settings, such as
      name, email/phone number
### [DASHBOARD] ###
   > ![PERMISSIONS][N/A]
   >> The dashboard.
### [REPORTS] ###
   > ![PERMISSIONS][CHIEFTAIN]
   >> Generate reports of checkouts and missing books and the like.
### [ROLES] ###
   > ![PERMISSIONS][MANAGE ROLES]
   >> View & edit roles for this location.
### [ACCOUNTS] ###
   > ![PERMISSIONS][ADMIN]
   >> View & manage accounts + roles for this location.
### [LOCATION] ###
   > ![PERMISSIONS][ADMIN]
   >> View & manage location info, including name, color scheme, picture...

**HELP**
> Help pages having to do with managing and using Booksy. May differ per role.

**ABOUT**
> A miscellaneous "about" page intended for the convenience of FBLA viewers.
Single-page, contains links to GitHub repo and AngularJS information and the
suchlike.
