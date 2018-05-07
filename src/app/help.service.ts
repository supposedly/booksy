import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { catchError, map, tap } from 'rxjs/operators';
import { Observable } from 'rxjs/Observable';
import { of } from 'rxjs/observable/of';

import { HttpOptions } from './classes';
const httpOptions = HttpOptions;

// Handles content-serving/-fetching on help articles.
@Injectable()
export class HelpService {
  private titlesURL = 'api/help/titles';
  private contentURL = 'api/help/content';
  private quickhelpURL = 'api/help/brief';
  
  constructor(private http: HttpClient) {}
  
  getArticles(): any {
    return this.http.get<any>(this.titlesURL).shareReplay();
  }
  
  getArticle(id): Observable<any> {
    return this.http.get<any>(this.contentURL, {params: {ID: id}});
  }
  
  getBrief(id): Observable<any> {
    return this.http.get<any>(this.quickhelpURL, {params: {ID: id}});
  }

}
