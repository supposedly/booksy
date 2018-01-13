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
  private suggestionURL: string = '/api/member/suggest';
  
  constructor(
    private http: HttpClient,
    private globals: Globals
  ) { }
  
  getAll(cont): Observable<any> {
    return this.http.get(this.membersURL, {params: {uid: this.globals.uID, cont: cont}});
  }
  
  getNotifs(username?: string): Observable<any> {
    return this.http.get<any>(this.notifURL, {params: {username: username?username:this.globals.username, lid: this.globals.lID}}).shareReplay();
  }
  
  getSuggestions(): Observable<any> {
    return this.http.get(this.suggestionURL, {params: {uid: this.globals.uID}});
  }
  
}
