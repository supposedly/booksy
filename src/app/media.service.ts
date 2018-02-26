import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { Observable } from 'rxjs/Observable';
import { of } from 'rxjs/observable/of';

import { MediaItem, MediaItemProxy, HttpOptions } from './classes';
const httpOptions = HttpOptions;

import { Globals } from './globals';

@Injectable()
export class MediaService {
  private infoURL = 'api/media/info';
  private statusURL = 'api/media/check';
  private holdURL = 'api/media/hold';
  private editItemURL = 'api/media/edit';
  private deleteItemURL = 'api/media/delete';
  private payFinesURL = 'api/media/clear-fines';

  constructor(
    private globals: Globals,
    private http: HttpClient
  ) {}
  
  /*
  class MediaItem {
    mid: string;
    type: mtype;
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
    return this.http.post<any>(this.holdURL, {mid: mID}, httpOptions);
  }
  
  editItem(item): Observable<any> {
    item.uid = this.globals.uID;
    item.type_ = item.type.name; // eh
    return this.http.post<any>(this.editItemURL, item, httpOptions);
  }
  
  deleteItem(mID): Observable<any> {
    return this.http.post<any>(this.deleteItemURL, {mid: mID}, httpOptions);
  }
  
  markFinesPaid(mID): Observable<any> {
    return this.http.post<any>(this.payFinesURL, {mid: mID}, httpOptions);
  }
  
}
