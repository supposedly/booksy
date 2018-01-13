import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { catchError, map, tap } from 'rxjs/operators';
import { Observable } from 'rxjs/Observable';
import { of } from 'rxjs/observable/of';

import { HttpOptions } from './classes';
const httpOptions: string = HttpOptions;

import { Globals } from './globals';


@Injectable()
export class LocationService {
  locItemsURL: string = '/api/location/media';
  searchURL: string = '/api/location/search';
  
  constructor(
    private globals: Globals,
    private http: HttpClient
  ) {}
  
  getAllMedia(cont): Observable<any> {
    return this.http.get<any>(this.locItemsURL, {params: {uid: this.globals.uID, cont: cont}});
  }
  
  searchMedia(cont=0, title=null, author=null, genre=null, type_=null): Observable<any> {
    return this.http.get<any>(this.searchURL, {
      params: {
        uid: this.globals.uID,
        cont: cont,
        title: title,
        author: author,
        genre: genre,
        media_type: type_
      }
    });
  }
  
}
