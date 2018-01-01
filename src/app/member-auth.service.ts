import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

import { LoggingService } from './logging.service';

import { Location, HttpOptions } from './classes';

import { catchError, map, tap } from 'rxjs/operators';
import { Observable } from 'rxjs/Observable';
import { of } from 'rxjs/observable/of';
import 'rxjs/add/operator/shareReplay';

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
  public uID: number;
  public lID: number;
  
  //these are potentially subject to change but can still be cached until they do
  public username: string;
  public rID: number;
  public phone: string;
  public email: string;
  
  private resjson;
  private verified;
  
  constructor(
    private http: HttpClient,
    private loggingService: LoggingService
  ) {
      this.isLocationRegistered()
        .subscribe(value => this.isRegistered = value);
  }
  
  resetCache(): void {
    this.username = null;
    this.rID = null;
    this.email = null;
    this.phone = null;

    this.getInfo()
      .subscribe(res => this.resjson = res.json());
    
    this.username = this.resjson.username;
    this.rID = this.resjson.rid;
    this.email = this.resjson.email;
    this.phone = this.resjson.phone
  }
  
  isLocationRegistered(): Observable<any> {
    return this.http.get<any>(this.locInfoURL).pipe(
      tap(_ => this.log(`inquired whether the location's IP is registered w/ booksy`)),
      catchError(this.handleError<any>(`requesting loc info`))
      )
  }
  
  getInfo(): Observable<any> {
    return this.http.get<any>(this.infoURL, {params: {uid: this.uID.toString()}}).pipe(
      tap(_ => this.log(`requested user info`)),
      catchError(this.handleError<any>(`refreshing`))
      )
      .shareReplay();
  }
  
  logIn(uid: string, password: string, lid?: string) {
    let ret = this.http.post<any>(this.authURL, {
      user_id: uid,
      password: password,
      lid: this.lID,
    }, httpOptions)
    let _; ret.subscribe(temp => _);
    if (_) {
      this.getInfo()
        .subscribe(res => this.resjson = res.json());
      this.uID = this.resjson.user_id;
      this.rID = this.resjson.rid;
      this.lID = this.resjson.lid;
      this.isCheckoutAccount = this.resjson.is_checkout;
      this.username = this.resjson.username;
      this.managesLocation = this.resjson.manages;
      this.email = this.resjson.email;
      this.phone = this.resjson.phone;
    }
    return ret;
  }
  
  verify(): boolean {
    this.http.get<any>(this.verifyURL).pipe(
      tap(_ => this.log(`verified current user's access token`)),
      catchError(this.handleError<any>(`verification`))
      )
      .subscribe(resp => this.verified = resp.json());
    if (!this.verified || !this.verified.valid) {
      this.http.get<any>(this.refreshURL).pipe(
        tap(_ => this.log(`found expired access token so attempted to refresh it`)),
        catchError(this.handleError<any>(`refreshing token`))
        )
        .subscribe(resp => this.verified = resp.json());
    }
    return this.verified && this.verified.length > 0;
  }
  
  isLibrary() {
    return this.http.get<any>(this.infoURL).pipe(
      tap(_ => this.log(`verified current user's access token`)),
      catchError(this.handleError<any>(`verification`))
      )
      .subscribe(resp => resp.json().isCheckoutAccount);
  }
  
  logout() {
    return this.http.post(this.logoutURL, httpOptions).pipe(
      tap(_ => this.log(`logged out`)),
      catchError(this.handleError<any>(`verification`))
    )
    .subscribe();
  }
  
  private log(message: string) {
    this.loggingService.add('memberAuthService just ' + message);
  }
  
  /* Handle Http operation that failed.
  * Let the app continue.
  * @param operation - name of the operation that failed
  * @param result - optional value to return as the observable result
  */
  private handleError<T> (operation = 'operation', result?: T) {
    return (error: any): Observable<T> => {

      console.error(error); // log to console

      this.log(`${operation} failed: ${error.message}`);

      // let app continue running
      return of(result as T);
    };
  }
}
