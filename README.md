# First: A Retrospective

## What is this?

This is my submission for [FBLA](https://fbla-pbl.org)'s 2017-18 *Coding & Programming* competition:
*Develop a database program to manage the issuance of books at a school library.*
An archive of the full prompt for my year can be viewed
[here](https://web.archive.org/web/20170818141449/http://www.fbla-pbl.org/competitive-event/coding-programming/).

Having missed the listed requirement that it "run standalone", I -- being able to use nothing but basic-intermediate Python, having
gotten started a few months prior writing [a discord.py bot](https://github.com/eltrhn/conwaylife-caterer) for my
CA-related discord server, and among other things not knowing what a class was -- naturally decided that the best way to tackle
this would be to make it a web-facing application. Keep in mind, I knew *jack* about *jack* at this point -- just thought it'd be
easier to do this way than to make it a desktop app for some reason. I also signed up initially to take on the FBLA "3D animation"
event, but dropped out after finishing maybe 4 seconds of my submission because I needed to dedicate my time to this thing.

A series of uninformed decisions and an acute desire to be able to use buzzwords like "asynchronous" in my presentation (because
I sort-of-knew asyncio from discord.py and because
[the rubric](http://www.fbla-pbl.org/media/Coding-and-Programming-FBLA-Rating-Sheet.pdf)
dedicates like thirty points to what mostly amounts to technical knowledge) led me to [sanic](https://github.com/channelcat/sanic)
as a backend framework and Angular 5 up front. If I were to start over now, however, I would use neither of these things; sanic's nice
but it's still in beta and has some big big big security holes, and a common complaint regarding Angular that I've seen is that
it's "bloated", so I'd love to try and get my feet wet with Vue (more elegant?) or React (more popular?) instead. That's not to
disparage Angular, though -- it worked and it worked well for me! It's just I only chose it because I was initially trying to
avoid installing Node so I went with AngularJS 1.6, but after not being able to understand *anything* from its docs and tutorials
I said "screw it" and got nvm & npm. I then neglected to check out alternatives to what I'd been doing, so I just moved up to Angular
5 and went on from there. (**Major** props to the Angular team for their "Tour of Heroes" tutorial,
by the way. I cannot stress this enough. It is absolutely brilliant and basically got me up and running with nearly
everything I needed to know for this whole project after only following it once. If only more intro docs could be that way!)

That was over my junior-year winter break (I write this as a now-rising senior starting off the last summer), and after about
a week of floundering getting acquainted with Angular and sanic I found my stride. At this point I was under the misconception that I had about
a month to finish, because nobody told me that my state's FBLA organization was actually deferring the judging of Coding & Programming submissions
until the date of the state-wide conference, not the prior regional conferences, so I figured I needed to put in work... and put it in I did,
because this project essentially became my life for a good while.
I didn't have anything else to do during break because all of my friends were traveling, so I was staying up twelve hours a day working on nothing
but this thing; I somehow absorbed Python quickly enough as I went along, so this project effectively took me from beginner-intermediate to
intermediate-advanced all on its own. That's really the only way to learn something, I think: throw yourself into it, milk what you do know to the
last drop, and Google everything you don't. I still wasn't done after break ended, so those twelve daily hours turned to six (give or take) as school
started and my grades started dropping. (They would have dropped anyway, though. I'm not big on doing homework... so if this hadn't been wasting my time
something else would have)

## What did this teach you?

- The importance of linting & a good editor. I did this whole thing in gedit, and once I finally moved up to VSCode + pylint and ESLint half of every file
was lit up in underlines like a squiggly Christmas tree.
- The importance of making informed decisions *from the start* of a project. I mentioned not wanting to use sanic if I were to start over; knowing what I
do now, I'd probably instead have chosen flask (as is tried and tested) with nginx to handle the actual server-y part of things, although if I were to start
over *right now* I might actually stick to asyncio and use this new [vibora](https://github.com/vibora-io/vibora) thing. Wasn't around when I started this
project, but it looks exciting!
- Continuing the above, the importance of planning. I'd say I did okay on some sub-fronts of this front and just-plain-awfully on others; the whole `spec/d+ds.md`
file was typed out before I started anything else (mostly in that "floundering" stage I mentioned above) and it helped guide me early on, but at the same time I had
a great, great, much-too-great quantity of such stupid flubs along the way as the following.
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

## Why are you pinning to an outdated version (and your own fork, no less!) of sanic-jwt?

It works, and sanic-jwt at the time didn't accommodate for a specific thing I needed (which I only needed because I went the lazy route with authentication;
go through the commit history of my fork and view my added comment for specific details) so I had to fork it, but I also saw that a big 1.0 release was incoming
so I didn't bother requesting to merge my changes back into the main and soon-to-be-outdated lib. Dunno.

## How did this do in competition?

I placed 5th after presenting at state; 4th and higher go to nationals, so I'd have been out of luck had the guy in 3rd place not dropped out for another
event he made it in (because you can only perform in one event at natls). That being done, I was the ad-hoc 4th-place competitor and got to attend the
national conference, which was an amazing experience! Unfortunately, however, my presentation failed to make it past the initial filtration round (in which
they culled the competition pool from 52 participants down to 12), and so in turn was not one of the 10 ultimate winners.

I probably know what went wrong with my nationals presentation -- was basically five slides of tech stuff and then only one minute of demo where I should
have dedicated more time to actually showing the judge what the webapp looked like, but then I couldn't connect to WiFi so even that last minute
where I demo'd the program flow and such did not occur. However, because I got my rubrics/scoresheets back at neither the state level *nor*
the national level, I unfortunately have no idea what regard the project judges held this submission in.

**Below is the original text of this README, as submitted to the FBLA judges prior to the national-level competition.**

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
