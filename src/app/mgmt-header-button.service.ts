import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { catchError, map, tap } from 'rxjs/operators';
import { Observable } from 'rxjs/Observable';
import { of } from 'rxjs/observable/of';

import { LoggingService } from './logging.service';

import { NavButton, HttpOptions } from './classes';

const httpOptions = HttpOptions;

@Injectable()
export class MgmtHeaderButtonService {
  private buttonsURL: string = 'stock/buttons/mgmt-header';
  private rID: string;
  
  constructor(
    private loggingService: LoggingService,
    private http: HttpClient,
  ) {}
  
  getButtons(uID: string): Observable<any> {
    return this.http.get<NavButton[]>(this.buttonsURL, {params: {uid: uID}}).pipe(
      tap(heroes => this.log(`fetch the management header buttons from remote server`)),
      catchError(this.handleError('getting management header buttons', []))
    );
  }
  
  private log(message: string, error?: boolean) {
    this.loggingService.add(error?'mgmtHeaderButtonService: ':'App just used a MgmtHeaderButtonService to ' + message);
  }
    
  private handleError<T> (operation = 'operation', result ?: T) {
    return (error: any): Observable<T> => {

      console.error(error); // log to console

      this.log(`${operation} failed: ${error.message}`, true);

      // Let the app keep running by returning an empty result.
      return of(result as T);
    };
  }
  

}
