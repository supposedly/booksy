import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

import { HttpOptions } from './classes';
import { Globals } from './globals';

import { Observable } from 'rxjs/Observable';
import { of } from 'rxjs/observable/of';

const httpOptions = HttpOptions;

// Controls what happens on the checkout homescreen
@Injectable()
export class CheckoutService {
  private checkoutURL = '/api/media/check/out';
  private checkinURL = '/api/media/check/in';
  
  constructor(
    private globals: Globals,
    private http: HttpClient
  ) {}
  
  checkOut(mID, username) {
    return this.http.post<any>(this.checkoutURL, {
      username: username,
      lid: this.globals.lID,
      mid: mID,
    }, httpOptions);
  }
  
  checkIn(mID, username) {
    return this.http.post<any>(this.checkinURL, {
      username: username,
      lid: this.globals.lID,
      mid: mID,
    }, httpOptions);
  }

}
