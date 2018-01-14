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
  private notifURL: string = 'api/member/notifications';
  private suggestionURL: string = 'api/member/suggest';
  private holdsURL: string = 'api/member/held';
  private itemsURL: string = 'api/member/checked-out';
  
  constructor(
    private http: HttpClient,
    private globals: Globals
  ) {}
  
  getNotifs(username?: string): Observable<any> {
    return this.http.get<any>(this.notifURL, {params: {username: username?username:this.globals.username, lid: this.globals.lID}}).shareReplay();
  }
  
  getSuggestions(): Observable<any> {
    return this.http.get<any>(this.suggestionURL, {params: {uid: this.globals.uID}});
  }
  
  getItems(): Observable<any> { // checked-out items, that is
    return this.http.get<any>(this.itemsURL, {params: {uid: this.globals.uID}});
  }
  
  getHolds(): Observable<any> {
    return this.http.get<any>(this.holdsURL, {params: {uid: this.globals.uID}});
  }
  
}
