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
  
  getInfo(mid: number): Observable<MediaItem> {
    const mediaInfoURL = '/api/media/info';
    this.http.get<any>(mediaInfoURL, {params: {mid: mid.toString()}}).pipe(
      );
    return null;
  }
  
}
