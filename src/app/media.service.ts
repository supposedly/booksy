import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { catchError, map, tap } from 'rxjs/operators';
import { Observable } from 'rxjs/Observable';
import { of } from 'rxjs/observable/of';

import { LoggingService } from './logging.service';

import { MediaItem, MediaItemProxy, HttpOptions } from './classes';
const httpOptions = HttpOptions;

import { Globals } from './globals';

@Injectable()
export class MediaService {
  private infoURL = 'api/media/info';
  private statusURL = 'api/media/check';
  private holdURL = 'api/media/hold';

  constructor(
    private globals: Globals,
    private http: HttpClient
  ) {}
  
  /*
  export class MediaItem {
    mid: string;
    type: string;
    isbn: string;
    lid: string;
    title: string;
    author: string;
    published: string;
    acquired: string;
  } 
  */
  
  getStatus(mID: string): Observable<any> {
    return this.http.get<any>(this.statusURL, {params: {mid: mID}});
  }
  
  getInfo(mID: string): Observable<MediaItemProxy> {
    return this.http.get<MediaItemProxy>(this.infoURL, {params: {mid: mID}});
  }
  
  placeHold(mID: string): Observable<any> {
    return this.http.post<any>(this.holdURL, {uid: this.globals.uID, mid: mID});
  }
  
}
