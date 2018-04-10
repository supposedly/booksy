import { Injectable } from '@angular/core';

@Injectable()
export class Globals {
  // info regarding currently-logged-in user
  uID: string; // user ID
  lID: string; // location ID
  rID: string; // role ID
  locname: string; // location name
  username: string;
  name: string; // user's full name
  email: string; // user's email (unimplemented)
  phone: string; // user's phone number (unimplemented)
  managesLocation: boolean; // whether user is administrator (whether they own the location)
  canReturnItems: boolean; // whether user is allowed to check items in
  isCheckoutAccount: boolean; // whether the user is actually the library-wide checkout account
  isLoggedIn = false; // whether the user is signed in (used in initial login)
  
  // user's role's permissions object
  perms: any; // corresponds to Perms.namemap as defined in PackedBigIntField (from core.py)
  
  // Whether to hide the homepage sidebar.
  // It's here instead of in sidebar.component.ts because the
  // setting should persist when the user switches between any
  // two of the three main header tabs; sidebar.component.ts
  // gets reloaded when this happens, so it wouldn't be
  // feasible to keep it there.
  hide = false;
  // messages displayed on checkout; same deal, if we didn't have them here then they'd
  // pop up again every time the page is reloaded, even if the user had X-ed them away
  checkoutMessages = null;
  // generic names for the Perms, Limits, and Locks attributes (shown as descriptions on the edit screens)
  attrs;
  
  // report data received from server
  reportData = null;
  reportDataSortedBy = null;
  
  // genres and media types of user's location
  locMediaTypes;
  locGenres;
  
  // all roles in location
  locRoles;
  
  // header color, customizable per location
  locColor = '#f7f7f7';
  locActiveColor = '#888';
  locDepressedColor = '#bfc8cc';
  
  // help article info (not the text content though, just title and ID)
  helpArticles;
}
