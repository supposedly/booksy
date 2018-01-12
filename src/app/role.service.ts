import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { catchError, map, tap } from 'rxjs/operators';
import { Observable } from 'rxjs/Observable';

import { Role, HttpOptions } from './classes';
const httpOptions = HttpOptions;

import { Globals } from './globals';

@Injectable()
export class RoleService {
  private roleInfoURL = '/api/roles/detail';
  private roleEditURL = '/api/roles/edit';
  private allRolesURL = '/api/location/roles';
  
  constructor(
    private globals: Globals,
    private http: HttpClient
  ) {}
  
  getAll(): Observable<any> {
    return this.http.get<any>(this.allRolesURL, {params: {uid: this.globals.uID}})
  }
  
  getArrs(rID): Observable<any> {
    return this.http.get<any>(this.roleInfoURL, {params: {rid: rID, uid: this.globals.uID}});
  }
  
  modify(rID, perms, maxes, locks) {
    return this.http.post(this.roleEditURL, {uid: this.globals.uID, rid: rID, seqs: {perms: perms, maxes: maxes, locks: locks}}, httpOptions);
  }
  
}
