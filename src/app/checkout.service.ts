import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

import { LoggingService } from './logging.service';
import { MemberAuthService } from './member-auth.service';

import { Observable } from 'rxjs/Observable';
import { of } from 'rxjs/observable/of';

@Injectable()
export class CheckoutService {
  private infoURL: string = '/media/check';
  private checkoutURL: string = '/media/check/out';
  private checkinURL: string = '/media/check/in';
  
  constructor(
    private http: HttpClient,
    private memberAuthService: MemberAuthService
  ) { }
  
  checkStatus(mid): Observable<any> {
    return //this.http.get<any>
  }
  
  checkOut(mid) {
    return //this.http.post
  }

}
