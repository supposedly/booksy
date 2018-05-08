import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

import { SetupService } from './setup.service';
import { RoleService } from './role.service';

import { HttpOptions } from './classes';
import { Globals } from './globals';

import { Observable } from 'rxjs/Observable';
import { of } from 'rxjs/observable/of';
import 'rxjs/add/operator/shareReplay';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/do';

const httpOptions = HttpOptions;

// Handles things related to authentication & login-session verification.
@Injectable()
export class MemberAuthService {
  private authURL = '/auth';
  private verifyURL = '/auth/verify';
  private infoURL = '/auth/me';
  private refreshURL = '/auth/refresh';
  private logoutURL = '/auth/logout';
  
  private locInfoURL = '/api/location/is-registered';
  
  // we can cache all of these because they're not going to change
  public isRegistered: boolean; // whether location IP is present in server db
  public isCheckoutAccount: boolean; // whether user is logged in as a library checkout acct or as a user
  public managesLocation: boolean;
  public uID: string;
  public lID: string;
  
  // these are potentially subject to change but can still be cached until they do
  public username: string;
  public rID: string;
  public phone: string;
  public email: string;
  
  private resjson;
  private verified;
  
  constructor(
    private globals: Globals,
    private http: HttpClient,
    private roleService: RoleService,
    private setupService: SetupService,
  ) {
      this.isLocationRegistered()
        .subscribe(value => this.isRegistered = value.registered, err => this.isRegistered = false);
  }
  
  isLocationRegistered(): Observable<any> {
    // Unused feature. Returns whether the logger-in's IP address is 'registered',
    // which was meant to allow users to not have to fill the 'location ID' box
    // when logging in at a computer physically in their library.
    return this.http.get<any>(this.locInfoURL);
  }
  
  getInfo(): Observable<any> {
    return this.http.get<any>(this.infoURL, {params: {uid: this.uID}})
    .shareReplay();
  }
  
  saveToGlobals(details): void {
    this.uID = details.user_id;
    
    this.globals.uID = details.user_id;
    this.globals.rID = details.rid;
    this.globals.lID = details.lid;
    this.globals.isCheckoutAccount = details.is_checkout;
    this.globals.username = details.username;
    this.globals.name = details.name;
    this.globals.managesLocation = details.manages;
    this.globals.locname = details.locname;
    this.globals.email = details.email;
    this.globals.phone = details.phone;
    
    if (details.user_id) {
      this.setupService.getAttrs(details.user_id);
      this.setupService.getPerms(details.user_id);
    }
  }
  
  storeMeInfo(): void {
    // On signin, globally store info pertaining to member
    // (so other components can access it).
    this.getInfo()
      .subscribe(res => {
        this.saveToGlobals(res.me);
        this.globals.isLoggedIn = true;
      }
    );
  }
  
  logIn(uid: string, password: string, lid?: string) {
    return this.http.post<any>(this.authURL, {
      user_id: uid,
      password: password,
      lid: this.lID ? this.lID : lid,
    }, httpOptions);
  }
  
  verify(): any {
    // Return whether the current user's session has expired (or whether they're
    // otherwise not supposed to be logged in) by sending the current access
    // token/refresh token to the server for JWT verification.
    return this.http.get<any>(this.verifyURL);
  }
  
  refresh(): any {
    // Fetch a new JWT "refresh token", which is a string of text that will be sent to
    // the server to let it know who we're logged in as. Occasionally this token expires,
    // so this endpoint "refresh"es the session by having the server create a new one.
    return this.http.post<any>(this.refreshURL, httpOptions);
  }
  
  logOut() {
    // Clear token data & login session.
    this.globals.isLoggedIn = false;
    return this.http.post(this.logoutURL, httpOptions)
      .subscribe(resp => this.globals.isLoggedIn = false, err => console.log(err));
  }

}
