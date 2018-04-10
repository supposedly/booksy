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
  private notifURL = 'api/member/notifications';
  private suggestionURL = 'api/member/suggest';
  private holdsURL = 'api/member/held';
  private clearHoldURL = 'api/member/clear-hold';
  private itemsURL = 'api/member/checked-out';
  private editMemberURL = 'api/member/edit';
  private editSelfURL = 'api/member/self';
  
  constructor(
    private http: HttpClient,
    private globals: Globals
  ) {}
  
  edit(member): Observable<any> {
    return this.http.post<any>(this.editMemberURL, {member: member});
  }
  
  editSelf(fullName, newpass, curpass) {
    return this.http.post<any>(this.editSelfURL, {
      fullname: fullName == this.globals.name ? null : fullName,
      newpass: newpass ? newpass : null,
      curpass: curpass
    });
  }
  
  getNotifs(username?: string): Observable<any> {
    return this.http.get<any>(this.notifURL, {params: {username: username ? username : this.globals.username, lid: this.globals.lID}}).shareReplay();
  }
  
  getSuggestions(): Observable<any> {
    return this.http.get<any>(this.suggestionURL);
  }
  
  getItems(uID): Observable<any> {
    // checked-out items
    return this.http.get<any>(this.itemsURL, {params: {member: uID || this.globals.uID}});
  }
  
  getHolds(uID): Observable<any> {
    return this.http.get<any>(this.holdsURL, {params: {member: uID || this.globals.uID}});
  }
  
  clearHold(mID): Observable<any> {
    return this.http.post<any>(this.clearHoldURL, {mid: mID}, httpOptions);
  }
  
}
