import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { Observable } from 'rxjs/Observable';
import { of } from 'rxjs/observable/of';

import { MediaItem, MediaItemProxy, HttpOptions } from './classes';
const httpOptions = HttpOptions;

import { Globals } from './globals';

@Injectable()
export class MediaTypeService {
  private loc = '/api/location/media/types';
  private infoURL: string = this.loc + '/info';
  private typeAddURL: string = this.loc + '/add';
  private typeRmURL: string = this.loc + '/remove';
  private typeEditURL: string = this.loc + '/edit';
  
  constructor(
    private globals: Globals,
    private http: HttpClient
  ) {}
  
  all(): Observable<any> {
    return this.http.get<any>(this.loc);
  }
  
  info(name): Observable<any> {
    return this.http.get<any>(this.infoURL, {params: {name: name}});
  }
  
  edit(name, limits, newName, unit): Observable<any> {
    return this.http.post<any>(this.typeEditURL, {edit: name, limits: limits, name: newName, unit: unit});
  }
  
  add(limits, name, unit): Observable<any> {
    return this.http.post<any>(this.typeAddURL, {add: {limits: limits, name: name, unit: unit}});
  }
  
  delete(name): Observable<any> {
    return this.http.post<any>(this.typeRmURL, {remove: name});
  }
}
