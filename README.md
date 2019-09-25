# First: A Retrospective

## What is this?

This is my submission for [FBLA](https://fbla-pbl.org)'s 2017-18 *Coding & Programming* competition:  
> *Develop a database program to manage the issuance of books at a school library.*

An archive of the full prompt for my year can be viewed
[here](https://web.archive.org/web/20170818141449/http://www.fbla-pbl.org/competitive-event/coding-programming/).

I totally missed the requirement that submissions "run standalone", so, naturally, I -- not knowing the first thing about how
to make a webapp -- decided I wanted to make a webapp. A strange desire to use buzzwords like "asynchronous" in my presentation,
followed by a series of solidly uninformed decisions, led me to use
[sanic](https://github.com/channelcat/sanic) for a backend framework and Angular 5 up front... I'd *probably* choose a
different stack if I were to start over this instant, although Angular's Tour of Heroes tutorial is still pretty fantastic.

That was at the start of my junior year of high school. I ended up working twelve hours a day on this over winter break (my
presentation judge at nationals did *not* believe that), mostly because I was hustling to finish in time for my FBLA-regionals
conference -- nobody had told me that the submission deadline was actually being put off for eight weeks! This was also my first
'real' development project, taking me from novice to intermediate-advanced-ish in Python over the course of a few months, and
I've put down some beginner's thoughts about the whole process below.

## What did this teach you?

- The importance of linting & a good editor. My entire first iteration/submission was written in gedit, of all things, and once I
finally moved up to VSCode + pylint/ESLint I found half of every file lit up in underlines like a squiggly Christmas tree.
- The importance of making informed decisions *from the start* of a project. I mentioned not wanting to use sanic if I were to start
over; knowing what I do now, I'd probably instead have chosen flask (tried and tested) plus nginx to handle the actual server-y
part of things... although if I were to start over *right now* I might actually stick to asyncio and use this new
[vibora](https://github.com/vibora-io/vibora) thing. Wasn't around when I started this project, but it looks exciting!
- Continuing the above: the importance of planning. I'd say I did okay on some sub-fronts of this front, and just plain-awfully on others; the whole `spec/d+ds.md` file was typed out before I started anything else (mostly in the preparatory desperate-floundering stage)
and it helped guide me early on, but at the same time I had a great, great, much-too-great quantity of such stupid flubs along the way
as:
  - Not actually validating passwords when I thought I was
  - Using a system for verifying sessions where the only things actually verified were that the user was (a) logged in, and (b) sending a valid User ID as
    part of their session info... which meant that you could use cURL or something to log in to any account, then once signed in start sending requests with
    the user ID of an admin (even if you were not logged in as an admin!) to perform any managerial action you wished to. This was because the JWT framework
    I used does/did not have an obvious way to retrieve someone's user info from their request/session objects, so I figured I could just have the frontend
    handle providing that info. Blech.
  - Writing SQL queries before I actually learned SQL and then not looking at them again until the night before due date (at *which* point I realized just how bad it was)
  - Completely forgetting to implement book renewals despite setting up all the visual machinery around it. Whoops.
  - Until the day before the national conference's due date, not verifying that the media item some user checked out was from the same library as the user (and, relatedly,
    making my DB table for "media" have a PK only of media ID rather than location ID + media ID, blech)
- Three-ish new languages: TypeScript/JavaScript + HTML + CSS to a reasonable degree as well as a lot of Angular-specific stuff; Python, to a higher-intermediate level
as mentioned; and SQL within Postgres.

## How did this do in competition?

I placed 5th after presenting at the state-level competition; 4th and higher go to nationals, so I'd have been out of luck had the
guy in 3rd place not dropped out for another event he placed in (because you can only perform in one event at natls). That being
done, I was the ad-hoc 4th-place competitor and got to attend the national conference, which by all measures was an *amazing*
experience -- but, sadly, I was not one of the 10 final winners.

I definitely know what went wrong with my nationals presentation -- it was essentially five slides of tech stuff and then
only one minute of demo where I should have dedicated more time to actually showing the judge what the webapp looked like,
but between BSing a little bit to clear the minimum time and then not even being able to connect to WiFi for the demo part,
it was overall a disappointing attempt. I could do better now!  
As for the actual website, despite the effort I put into it, I found out a few months after nationals
that it barely managed an all-around average set of scores (with some dips below average, even). A little bit disheartening -- I
was quite confident about some of it, and there are parts on which I really believed I'd done exceptionally well -- but that's
the way it goes. Here's my scoresheet, transcribed using a 4-point scale where 2 is "below", 3 is "meeting", and 4 is "exceeding"
expectations:

| (Sub-)Category | Score | Notes |
|---|---|---|
| **Program Readability** | - | - |
| Appropriate identifiers used for variables, constants, arrays, objects, etc. | 3 |  |
| Commentary provided is readable, useful, and complete | 2.5 | 3 from one judge, 2 from the other |
|  General program documentation is readable, useful, and complete | 3 |  |
| **Program Structure and Content** | - | - |
| Program is concise and does not contain unnecessary complexity | 3 |  |
| Data storage is appropriate | 3 |  |
| Program use follows a logical sequence | 3 |  |
| **Usability & Results** | - | - |
| Program use and navigation | 2.5 | 2 from one judge, 3 from the other |
| Program Results | 3 |  |
| Output Reports | 3 |  |

### **Below is the original text of this README, submitted to the FBLA judges prior to the national-level competition.**

# Booksy

Hello! Please visit this URL: https://booksy-db.herokuapp.com

## Accounts

You can register your own sandbox via the "Sign your library up" button from the login page, but a demo library has
been prepared nonetheless under the inspired name of *Fort Blaine Law Academy*. You can access it by signing in in with a
**Location ID** of 1 and one of the following strings in both the userID and password fields (same user + pass):
* `fbla-demo-admin` to use the administrator account, from which you may add users and whatnot and do essentially everything.
* `fbla-demo-teacher` to use an account given the Organizer role (from which one can view reports and return
   items, but without any managerial functionality besides user management)
* `fbla-demo-user` to use a user account given zero permissions except to find and check out media (i.e. given
   the Subscriber role)
* `fbla-demo-checkout` to use the self-checkout account (Ctrl+F **checkout** to see here below what is meant by this).
 
Note that, of course, additional accounts of any stature can be created by the `fbla-demo-admin` user, and by any member with the 'manage members' permission.

## Browser compatibility
### [Windows XP](https://i.imgur.com/CEH2k7r.png):
- **Firefox 52**
    - This is the only "modern" browser release available on XP, and it also appears to be the only browser on XP compatible with Angular 5.

### A modern OS:
- **Chrome 57+** (preferred)
- Safari 10.1
    - ...perhaps below? Could not conduct comprehensive testing, and was only able to try v5.7 (incompatible) and v10.1 (compatible)
- Firefox 52+
- Opera 44+

### Android/iOS (no preference):
- Firefox
- Chrome
- Opera
- Opera Mini

**Not supported:** Microsoft Edge, Internet Explorer

## The code

Visit the [ABOUT](https://booksy-db.herokuapp.com/about) tab up top to see my credits and code, the latter being here at https://gitlab.com/hdtrhn/fbla-webapp.

It's a bit much to slog through, but I hope my comments and docstrings are sufficient.

To aid you in reviewing the project, here's a general what-to-look-for and a brief explanation of its structure:
* The server back-end code is in the `server.py` file of the root directory and in the `backend/` folder of the same.  
  Within the backend folder, each sub-folder in the `blueprints/` directory corresponds to a path in the site's API;
  for example, to see which sections of the "HOME" page the current user can navigate to via the sidebar, the webapp sends a request to the URL
  `/stock/buttons/home-sidebar`.  
  This is reflected in the back-end directory structure; when this request is received, it's routed to the file in
  `backend/blueprints/stock/buttons.py`, and is handled within this file by the function decorated `@btn.get('/sidebar')`.
* The part of the back-end code that does the actual accessing of the PostgreSQL database is contained within
  the `backend/typedef/` directory, where I've defined objects for locations (i.e. libraries registered with Booksy),
  users (anybody logged in), media items, media types, and roles (user authorization property containers).
* The front end, whose structure was generated by the Angular CLI shipped with Angular 5 (though of course the CLI
  does not do any actual coding), is contained in the `src/app` directory.
* Within `src/app`: the `.service.ts` files are what Angular calls Services, from which I do the actual
  communication between the front and back end. These Services fetch information for/from the Components to pass between them and the backend
  over the internet.
* The files in the sub-folders of `src/app` are Components (as indicated by the word `.component` in their
  filename), which define the logic for pages served to the end user.  
  Files that end in `.component.ts` are the TypeScript code that grabs info from the Services to pass to their corresponding
  `.component.html` file, and the latter contains the HTML shown on the actual page. (If the HTML is short enough, it may
  also be placed within the `.component.ts` file after the `template:` line.)
* Any further questions about the project structure of an Angular app can be answered better than me by
  https://angular.io/docs and https://angular.io/tutorial.
* Also! For the Python route-handler files, don't be confused by the 'random' asterisks in function definitions -- they're only there
  so I could visually tell apart the 'universal' parameters (location, role, media, user, etc., placed before the asterisk) from ones
  specific to that function. The asterisk's usual purpose is to differentiate positional
  arguments from keyword arguments, but this doesn't apply here because my rqst\_get and uid\_get decorators pass everything in
  as a keyword argument anyway.


## Account types

Visit the [HELP](https://booksy-db.herokuapp.com/help) tab, next to the [ABOUT](https://booksy-db.herokuapp.com/about) tab, for detailed info.
I'll repeat some of the HELP info below --
 
There are two basic account types:
1. A checkout account, which is one shared by all members of the library (or the school, as it were) and from which any
member may enter their username to check out a book; this is my implementation of universal self-checkout (intended
to be used by leaving it up on a computer at the front desk of a library), and may be used by anybody at any time as
long as they know their username and the ID of the book they'd like to check out.  
...It's somewhat useless in its current
state because we don't have actual tangible books to use; in an ideal system, the user would scan the item's physical
barcode after entering their username, then just hit 'Submit' and be done. As it is now, however,
you must first have memorized the book's barcode/ID (fortunately an easy task, though -- they haven't hit 3 digits yet!)
by searching it up from your own account before going to the checkout account, and at that point you
may as well just check it out from your own account and be done with it.
2. A 'user' account, which is one that may access info about the library and such. Pretty standard fare.  
'User' accounts are given permissions by proxy of the Role system, and these permissions determine how much
functionality they get out of the webapp. I encourage you to play around by logging into the admin account and
seeing what permissions and roles you can assign.
 
Hope that covers everything you need to know. Again, read the HELP articles for more.

## Session timeout (bad)

Heroku, the platform-as-a-service host I am running the webapp on, forcibly idles projects hosted on their free tier
(as mine is!) after 30 minutes of disuse; to do this it shuts down the server program entirely and only restarts it
when a new request comes in. This means that, if you are the only current user and you
remain idle on a page for about half an hour, the application might implicitly log you out and forget your session info.

Fortunately, there are services that keep your application alive by sending it a ping every so often -- I'm using one --
but they aren't foolproof, and the application might shut down temporarily anyway . If you're ever browsing and see
something like "Auth required." or see some info not pop up when it should, this is likely the cause; just log out
and back in, or refresh the page, and things will be back to normal.

## Extras
- See `spec/d+ds.md` for a slightly-outdated-but-still-decently-accurate rundown of how the app interacts with the end-user. (It was my initial
  planning document where I got my thoughts down, but I deviated a little from it in actually applying things)
- See the "General UX overview" help article for a rundown of how to navigate the application and where to look for certain functionality.

Thank you :)
