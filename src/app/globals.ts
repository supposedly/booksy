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
  
  // whether to hide the homepage sidebar.
  // It's here instead of in sidebar.component.ts so that the
  // setting persists even when the user switches to/from any
  // of the three main tabs.
  hide: boolean = false;
}
