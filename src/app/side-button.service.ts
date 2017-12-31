import { Injectable } from '@angular/core';

import { HttpClient } from '@angular/common/http';

import { catchError, map, tap } from 'rxjs/operators';
import { Observable } from 'rxjs/Observable';
import { of } from 'rxjs/observable/of';

import { SideButton, HttpOptions } from './classes';
import { MemberAuthService } from './member-auth.service';
import { LoggingService } from './logging.service';

const httpOptions = HttpOptions;

@Injectable()
export class SideButtonService {
  private buttonsURL: string = 'stock/buttons/home-sidebar';
  private rID: number;
  
  constructor(
    private loggingService: LoggingService,
    private http: HttpClient,
    private memberAuthService: MemberAuthService,
  ) {
      this.memberAuthService.getRID()
        .subscribe(rid => this.rID = rid);
  }
  
  private log(message: string) {
    this.loggingService.add('App just used a SideButtonService to ' + message);
  }
  
  getButtons(): Observable<SideButton[]> {
    return this.http.get<SideButton[]>(this.buttonsURL, {params: {rid: this.rID.toString()}}).pipe(
      tap(heroes => this.log(`fetch the sidebar buttons from remote server`)),
      catchError(this.handleError('getButtons', []))
    );
  }
  
  private handleError<T> (operation = 'operation', result ?: T) {
    return (error: any): Observable<T> => {

      // TODO: send the error to remote logging infrastructure
      console.error(error); // log to console instead

      // TODO: better job of transforming error for user consumption
      this.log(`${operation} failed: ${error.message}`);

      // Let the app keep running by returning an empty result.
      return of(result as T);
    };
  }
  

}
