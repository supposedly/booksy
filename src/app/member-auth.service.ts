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
    return this.http.get<any>(this.locInfoURL);
  }
  
  getInfo(): Observable<any> {
    return this.http.get<Observable<any>>(this.infoURL, {params: {uid: this.uID}})
      .shareReplay();
  }
  
  saveToGlobals(dts): void {
    this.uID = dts.user_id;
    
    this.globals.uID = dts.user_id;
    this.globals.rID = dts.rid;
    this.globals.lID = dts.lid;
    this.globals.isCheckoutAccount = dts.is_checkout;
    this.globals.username = dts.username;
    this.globals.name = dts.name;
    this.globals.managesLocation = dts.manages;
    this.globals.locname = dts.locname;
    this.globals.email = dts.email;
    this.globals.phone = dts.phone;
    
    if (dts.user_id) {
      this.setupService.getAttrs(dts.user_id);
      this.setupService.getPerms(dts.user_id);
    }
  }
  
  storeMeInfo(): void { // store info about currently-logged-in user on login
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
    return this.http.get<any>(this.verifyURL);
  }
  
  refresh(): any {
    return this.http.post<any>(this.refreshURL, httpOptions);
  }
  
  logOut() {
    this.globals.isLoggedIn = false;
    return this.http.post(this.logoutURL, httpOptions)
      .subscribe(resp => this.globals.isLoggedIn = false, err => console.log(err));
  }
  
}
