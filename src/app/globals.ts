import { Injectable } from '@angular/core';

@Injectable()
export class Globals {
  // info regarding currently-logged-in user
  uID: string;
  lID: string;
  rID: string;
  locname: string;
  username: string;
  name: string;
  email: string;
  phone: string;
  managesLocation: boolean;
  canReturnItems: boolean;
  isCheckoutAccount: boolean;
  isLoggedIn: boolean = false;
  
  // user's role's permissions object
  perms: any;
  
  // Whether to hide the homepage sidebar.
  // It's here instead of in sidebar.component.ts because the
  // setting should persist when the user switches between any
  // two of the three main header tabs; sidebar.component.ts
  // gets reloaded when this happens, so it wouldn't be
  // feasible to keep it there.
  hide: boolean = false;
  // messages displayed on checkout; same deal, if we didn't have them here then they'd
  // pop up again every time the page is reloaded, even if the user had X-ed them away
  checkoutMessages = null;
  // generic names for the Perms, Maxes, and Locks attributes (shown as descriptions on the edit screens)
  attrs: any;
  
  // report data received from server
  reportData = null;
  reportDataSortedBy = null;
  
  // genres and media types of user's location
  locMediaTypes;
  locGenres;
  
  // all roles in location
  locRoles;
  
  // help article info (not the text content though)
  helpArticles;
}
