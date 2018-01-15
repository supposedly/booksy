import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { catchError, map, tap } from 'rxjs/operators';
import { Observable } from 'rxjs/Observable';
import { of } from 'rxjs/observable/of';

import { HttpOptions } from './classes';
const httpOptions = HttpOptions;

import { Globals } from './globals';


@Injectable()
export class LocationService {
  loc: string = 'api/location';
  private locItemsURL: string = this.loc + '/media';
  private searchURL: string = this.loc + '/media/search';
  private allMembersURL: string = this.loc + '/members';
  private memberInfoURL: string = this.loc + '/members/info';
  private createMemberURL: string = this.loc + '/members/add';
  private deleteMemberURL: string = this.loc + '/members/remove';
  private createItemURL: string = this.loc + '/media/add';
  private delItemURL: string = this.loc + '/media/remove';
  private editMemberURL: string = 'api/member/edit';
  
  constructor(
    private globals: Globals,
    private http: HttpClient
  ) {}
  
  getMemberInfo(uID): Observable<any> {
    return this.http.get(this.memberInfoURL, {params: {uid: this.globals.uID, check: uID}});
  }
  
  getAllMembers(cont): Observable<any> {
    return this.http.get(this.allMembersURL, {params: {uid: this.globals.uID, cont: cont}});
  }
  
  getAllMedia(cont): Observable<any> {
    return this.http.get<any>(this.locItemsURL, {params: {uid: this.globals.uID, cont: cont}});
  }
  
  searchMedia(cont=0, title=null, author=null, genre=null, type_=null): Observable<any> {
    return this.http.get<any>(this.searchURL, {
      params: {
        uid: this.globals.uID,
        cont: cont.toString(),
        title: title?title:null,     // doesn't produce the expected result if I don't do the ternary :thonk:
        author: author?author:null,  // It may also be that I had another error that I fixed at the same time
        genre: genre?genre:null,     // as I was messing with the ternary, and so I myself am erroneously
        media_type: type_?type_:null // ascribing the error's cause to something to do with the ternary...
      }
    });
  }
  
  deleteMember(uID): Observable<any> {
    return this.http.post<any>(this.deleteMemberURL, {uid: this.globals.uID, remove: uID});
  }
  
  editMember(member): Observable<any> {
    return this.http.post<any>(this.editMemberURL, {uid: this.globals.uID, member: member});
  }

  createMember(member): Observable<any> {
    return this.http.post<any>(this.createMemberURL, {uid: this.globals.uID, member: member}, httpOptions);
  }
  
  deleteItem(mID): Observable<any> {
    return this.http.post<any>(this.delItemURL, {uid: this.globals.uID, mid: mID}, httpOptions);
  }
  
  addItem(item): Observable<any> {
    item.uid = this.globals.uID; // so I can grab everything in the backend at once
    return this.http.post<any>(this.createItemURL, item, httpOptions);
  }
  
  removeMember(uID): Observable<any> {
    return this.http.post<any>(this.deleteMemberURL, {uid: this.globals.uID, member: uID}, httpOptions);
  }
  
}
