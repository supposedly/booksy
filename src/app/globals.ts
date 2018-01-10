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
  isCheckoutAccount: boolean;
  isLoggedIn: boolean = false;
  
  // Whether to hide the homepage sidebar.
  // It's here instead of in sidebar.component.ts because the
  // setting should persist when the user switches between any
  // two of the three main header tabs; sidebar.component.ts
  // gets reloaded when this happens, so it wouldn't be
  // feasible to keep it there.
  hide: boolean = false;
  // messages displayed on checkout; same deal
  checkoutMessages = null;
}
