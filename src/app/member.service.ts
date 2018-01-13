import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { catchError, map, tap } from 'rxjs/operators';
import { Observable } from 'rxjs/Observable';
import { of } from 'rxjs/observable/of';
import 'rxjs/add/operator/shareReplay';

import { Globals } from './globals';

import { HttpOptions } from './classes';
const httpOptions = HttpOptions;

@Injectable()
export class MemberService {
  private notifURL: string = '/api/member/notifications';
  private membersURL: string = '/api/location/members';
  
  constructor(
    private http: HttpClient,
    private globals: Globals
  ) { }
  
  getNotifs(uID?: string): Observable<any> {
    return this.http.get<any>(this.notifURL, {params: {uid: uID?uID:this.globals.uID}}).shareReplay();
  }
  
  getAll(cont): Observable<any> {
    return this.http.get(this.membersURL, {params: {uid: this.globals.uID, cont: cont}});
  }
  
}
