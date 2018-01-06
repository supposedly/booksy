import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

import { LoggingService } from './logging.service';

import { Location, HttpOptions } from './classes';
import { Globals } from './session-info-globals';

import { catchError, map, tap } from 'rxjs/operators';
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
  
  //we can cache all of these because they're not going to change
  public isRegistered: boolean; //whether location IP is present in server db
  public isCheckoutAccount: boolean; //whether user is logged in as a library checkout acct or as a user
  public managesLocation: boolean;
  public uID: string;
  public lID: string;
  
  //these are potentially subject to change but can still be cached until they do
  public username: string;
  public rID: string;
  public phone: string;
  public email: string;
  
  private resjson;
  private verified;
  
  constructor(
    private globals: Globals,
    private http: HttpClient,
    private loggingService: LoggingService
  ) {
      this.isLocationRegistered()
        .subscribe(value => this.isRegistered = value['registered'], err => this.isRegistered = false);
  }
  
  resetCache(): void {
    this.username = null;
    this.rID = null;
    this.email = null;
    this.phone = null;
    
    this.getInfo()
      .subscribe(res => this.resjson = res, err => this.resjson=null);
    // FIXME: THIS DOES NOT WORK AS I PREVIOUSLY RAN INTO
    // BECAUSE SUBSCRIPTIONS ARE NOT WAITED UPON
    if (this.resjson) {
      this.username = this.resjson.username;
      this.rID = this.resjson.rid;
      this.globals.rID = this.rID;
      this.email = this.resjson.email;
      this.phone = this.resjson.phone
    }
  }
  
  isLocationRegistered(): Observable<any> {
    return this.http.get<any>(this.locInfoURL).pipe(
      tap(_ => this.log(`inquired whether the location's IP is registered w/ booksy`)),
      )
  }
  
  getInfo(): Observable<any> {
    return this.http.get<Observable<any>>(this.infoURL, {params: {uid: this.uID}}).pipe(
      tap(_ => this.log(`requested user info`)),
      )
      .shareReplay();
  }
  
  logIn(uid: string, password: string, lid?: string) {
    let ret = this.http.post<any>(this.authURL, {
      user_id: uid,
      password: password,
      lid: this.lID ? this.lID : lid,
    }, httpOptions)
    ret.subscribe(_ => {
      if (_) {
        this.getInfo()
          .subscribe(res => {
            this.uID = res.me.user_id;
            this.globals.uID = this.uID;
            
            this.rID = res.me.rid;
            this.globals.rID = this.rID;
            
            this.lID = res.me.lid;
            this.globals.lID = this.lID;
            
            this.isCheckoutAccount = res.me.is_checkout;
            this.username = res.me.username;
            this.managesLocation = res.me.manages;
            this.email = res.me.email;
            this.phone = res.me.phone;
            this.globals.isLoggedIn = true;
            this.resjson = res.me;
          }
        );
      }
    });
    return ret;
  }
  
  verify(): boolean {
    this.http.get<any>(this.verifyURL).pipe(
      tap(_ => this.log(`verified current user's access token`)),
      )
      .subscribe(resp => this.verified = resp, err => {console.log(err); this.verified = false});
    if ((!this.verified) || !this.verified['valid']) {
      this.http.post<any>(this.refreshURL, httpOptions).pipe(
        tap(_ => this.log(`found expired access token so attempted to refresh it`)),
        )
        .subscribe(resp => this.verified = resp, err => {console.log(err); this.verified = false});
    }
    this.globals.isLoggedIn = this.verified && (this.verified.access_token || this.verified.valid);
    return this.globals.isLoggedIn
  }
  
  isLibrary() {
    return this.http.get<any>(this.infoURL).pipe(
      tap(_ => this.log(`verified current user's access token`)),
      )
      .subscribe(resp => resp.isCheckoutAccount);
  }
  
  logOut() {
    return this.http.post(this.logoutURL, httpOptions).pipe(
      tap(_ => this.log(`logged out`)),
    )
    .subscribe(resp => this.globals.isLoggedIn = false, err => console.log(err));
  }
  
  private log(message: string, error?: boolean) {
    this.loggingService.add((error?'memberAuthService: ':'memberAuthService just ') + message);
  }
}
