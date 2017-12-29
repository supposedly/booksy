``One more bulleted design-spec list`` for booksy-db
1. App serves login page.
  - Before serving it, app sends request to `/api/location/is-registered`
  - If server responds false, show both UID and LID fields
  - Else if server responds true, show only UID field with location's colour scheme
2. User logs in.
  - App POSTs the provided LID & UID to /auth.
  - Hopefully everything works and sanic-jwt stores the JWT cookie and whatnot
  - From here on out, the app will use its AuthGuard to GET /auth/verify
    before every page visit to check whether the user is logged in.
4. App fetches relevant buttons.
  - App GETs its header buttons and sidebar buttons from `/stock/main-header`
    and `/stock/home-sidebar`.
  - 
3. App serves starting page.
  - User will be routed after login to the Checkout page in the Home tab.
  - From here up until list item `4.`, this document will attempt to
    outline the details of how the front- and back-end will interact in
    the sidebar pages of the Home tab.
  > [CHECKOUT]
    - App will route user to a screen with the large text "Welcome" and
      small text "Check out or return a book".
