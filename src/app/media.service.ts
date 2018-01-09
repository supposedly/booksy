import { Injectable } from '@angular/core';

import { HttpClient } from '@angular/common/http';

import { catchError, map, tap } from 'rxjs/operators';
import { Observable } from 'rxjs/Observable';
import { of } from 'rxjs/observable/of';

import { MediaItem, HttpOptions } from './classes';
import { LoggingService } from './logging.service';

const httpOptions = HttpOptions;

@Injectable()
export class MediaService {
  private infoURL = '/api/media/info';
  private statusURL = '/api/media/check';

  constructor(
    private http: HttpClient
  ) { }
  
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
  
  getInfo(mID: string): Observable<MediaItem> {
    const mediaInfoURL = '/api/media/info';
    return this.http.get<any>(this.infoURL, {params: {mid: mID}});
  }
  
}
