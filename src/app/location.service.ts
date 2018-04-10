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
  private loc = 'api/location';
  
  private locSignupURL: string = this.loc + '/signup';
  private locEditURL: string = this.loc + '/edit';
  
  private locItemsURL: string = this.loc + '/media';
  private searchURL: string = this.loc + '/media/search';
  
  private allRolesURL = this.loc + '/roles';
  private filteredRolesURL = this.allRolesURL + '/filtered';
  
  private allMembersURL: string = this.loc + '/members';
  private memberInfoURL: string = this.loc + '/members/info';
  private createMemberURL: string = this.loc + '/members/add';
  private deleteMemberURL: string = this.loc + '/members/remove';
  
  private locMedia: string = this.loc + '/media';
  
  private createItemURL: string = this.locMedia + '/add';
  private delItemURL: string = this.locMedia + '/remove';
  
  private editGenreURL: string = this.locMedia + '/genres/edit';
  private delGenreURL: string = this.locMedia + '/genres/remove';
  
  constructor(
    private globals: Globals,
    private http: HttpClient
  ) {}
  
  register(email, locname, color, adminname) {
    return this.http.post<any>(this.locSignupURL, {
      email: email,
      locname: locname,
      color: color,
      adminname: adminname
    });
  }
  
  edit(locname, color, fine_amt, fine_interval, checkoutpw) {
    return this.http.post<any>(this.locEditURL, {
      locname: locname,
      color: color,
      fine_amt: fine_amt,
      fine_interval: fine_interval,
      checkoutpw: checkoutpw
    });
  }
  
  getLocInfo() {
    return this.http.get<any>(this.loc);
  }
  
  getMemberInfo(uID): Observable<any> {
    return this.http.get(this.memberInfoURL, {params: {check: uID}});
  }
  
  getAllMembers(cont): Observable<any> {
    return this.http.get(this.allMembersURL, {params: {cont: cont}});
  }
  
  getAllMedia(cont): Observable<any> {
    return this.http.get<any>(this.locItemsURL, {params: {cont: cont}});
  }
  
  getAllRoles(): Observable<any> {
    return this.http.get<any>(this.allRolesURL);
  }
  
  getFilteredRoles(): Observable<any> {
    return this.http.get<any>(this.filteredRolesURL);
  }
  
  searchMedia(cont= 0, title= null, author= null, genre= null, type_= null): Observable<any> {
    return this.http.get<any>(this.searchURL, {
      params: {
        cont: cont.toString(),
        title: title ? title : null,     // doesn't produce the expected result if I don't do the ternary, hmm.
        author: author ? author : null,  // It may also be that I had another error that I fixed at the same time
        genre: genre ? genre : null,     // as I was messing with the ternary, and so I myself am erroneously
        media_type: type_ ? type_ : null // ascribing the error's cause to something to do with the ternary...
      }
    });
  }
  
  createMember(member): Observable<any> {
    return this.http.post<any>(this.createMemberURL, {member: member}, httpOptions);
  }
  
  deleteItem(mID): Observable<any> {
    return this.http.post<any>(this.delItemURL, {mid: mID}, httpOptions);
  }
  
  addItem(item): Observable<any> {
    item.uid = this.globals.uID; // so I can grab everything from backend at once
    item.media_type = item.type; // meh, just for name conflict in python (not the most elegant way of handling)
    return this.http.post<any>(this.createItemURL, item, httpOptions);
  }
  
  removeMember(uID): Observable<any> {
    return this.http.post<any>(this.deleteMemberURL, {member: uID}, httpOptions);
  }
  
  editGenre(genre, newname): Observable<any> {
    return this.http.post<any>(this.editGenreURL, {genre: genre, to: newname}, httpOptions);
  }
  
  removeGenre(genre): Observable<any> {
    return this.http.post<any>(this.delGenreURL, {genre: genre});
  }
  
}
