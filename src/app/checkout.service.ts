import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

import { MemberAuthService } from './member-auth.service';
import { LoggingService } from './logging.service';
import { HttpOptions } from './classes';
import { Globals } from './globals';

import { Observable } from 'rxjs/Observable';
import { of } from 'rxjs/observable/of';

const httpOptions = HttpOptions;

@Injectable()
export class CheckoutService {
  private checkoutURL: string = '/api/media/check/out';
  private checkinURL: string = '/api/media/check/in';
  
  constructor(
    private http: HttpClient,
    private globals: Globals,
    private memberAuthService: MemberAuthService
  ) { }
  
  checkOut(mID, uID) {
    return this.http.post<any>(this.checkoutURL, {
      uid: uID,
      mid: mID,
    }, httpOptions)
  }
  
  checkIn(mID, uID) {
    return this.http.post<any>(this.checkinURL, {
      uid: uID,
      mid: mID,
    }, httpOptions)
  }

}
