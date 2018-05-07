import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { catchError, map, tap } from 'rxjs/operators';
import { Observable } from 'rxjs/Observable';

import { Role, HttpOptions } from './classes';
const httpOptions = HttpOptions;

import { Globals } from './globals';

// Handles 
@Injectable()
export class RoleService {
  private roleInfoURL = '/api/roles/detail';
  private roleEditURL = '/api/roles/edit';
  private roleDelURL = '/api/roles/delete';
  private roleCreateURL = '/api/location/roles/add';
  
  constructor(
    private globals: Globals,
    private http: HttpClient
  ) {}
  
  getArrs(rID): Observable<any> {
    // Grab the info returned by Role.to_dict(), such as name & perms/limits/locks
    return this.http.get<any>(this.roleInfoURL, {params: {rid: rID}});
  }
  
  modify(rID, name, perms, limits, locks): Observable<any> {
    // Edit a given role with the given attributes. nulls accepted.
    return this.http.post(this.roleEditURL, {rid: rID, name: name, seqs: {perms: perms, limits: limits, locks: locks}}, httpOptions);
  }
  
  create(name, perms, limits, locks): Observable<any> {
    // Create a new role in the current library with the given attributes, returning its role ID.
    // (this really should be in locationService)
    return this.http.post(this.roleCreateURL, {name: name, seqs: {perms: perms, limits: limits, locks: locks}}, httpOptions);
  }
  
  delete(rID): Observable<any> {
    // Delete a role entirely.
    return this.http.put(this.roleDelURL, {rid: rID});
  }
  
}
