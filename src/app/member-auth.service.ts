import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

import { LoggingService } from './logging.service';

import { Location, HttpOptions } from './classes';
import { Globals } from './globals';

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
        .subscribe(value => this.isRegistered = value.registered, err => this.isRegistered = false);
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
  
  storeMeInfo(): void {
    this.getInfo()
      .subscribe(res => {
        this.globals.uID = res.me.user_id;
        this.globals.rID = res.me.rid;
        this.globals.lID = res.me.lid;
        this.globals.isCheckoutAccount = res.me.is_checkout;
        this.globals.username = res.me.username;
        this.globals.managesLocation = res.me.manages;
        this.globals.email = res.me.email;
        this.globals.phone = res.me.phone;
        this.globals.isLoggedIn = true;
      }
    );
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
            this.globals.uID = res.me.user_id;
            this.globals.rID = res.me.rid;
            this.globals.lID = res.me.lid;
            this.globals.isCheckoutAccount = res.me.is_checkout;
            this.globals.username = res.me.username;
            this.globals.managesLocation = res.me.manages;
            this.globals.email = res.me.email;
            this.globals.phone = res.me.phone;
            this.globals.isLoggedIn = true;
          }
        );
      } else { this.globals.isLoggedIn = false; }
    });
    return ret;
  }
  
  verify(): any /* boolean */ {
    this.http.get<any>(this.verifyURL).pipe(
      tap(_ => this.log(`verified current user's access token`)))
      .subscribe(
        resp => {
          this.globals.isLoggedIn = resp && resp.valid;
          if (this.globals.isLoggedIn) {
            return true;
          } else {
            this.http.post<any>(this.refreshURL, httpOptions).pipe(
              tap(_ => this.log(`found expired access token so attempted to refresh it`)))
              .subscribe(
                resp => {
                  this.globals.isLoggedIn = resp && (resp.access_token || resp.valid);
                  return this.globals.isLoggedIn;
                }, err => {
                  console.log(err);
                  this.globals.isLoggedIn = false;
                  return false;
                }
            );
          }
        }, err => {
          console.log(err);
          this.globals.isLoggedIn = false;
          return false;
        }
    );
    return this.globals.isLoggedIn; //synchronicity in an async function? yikes (but it works well)
  }
  
  logOut() {
    this.globals.isLoggedIn = false
    return this.http.post(this.logoutURL, httpOptions).pipe(
      tap(_ => this.log(`logged out`)),
    )
    .subscribe(resp => this.globals.isLoggedIn = false, err => console.log(err));
  }
  
  private log(message: string, error?: boolean) {
    this.loggingService.add((error?'memberAuthService: ':'memberAuthService just ') + message);
  }
}
