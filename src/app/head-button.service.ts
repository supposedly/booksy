import { Injectable } from '@angular/core';

import { HttpClient } from '@angular/common/http';

import { catchError, map, tap } from 'rxjs/operators';
import { Observable } from 'rxjs/Observable';
import { of } from 'rxjs/observable/of';

import { NavButton } from './classes';
import { LoggingService } from './logging.service';

@Injectable()
export class HeadButtonService {
  private buttonsURL = 'stock/buttons/main-header';
  
  constructor(
    private loggingService: LoggingService,
    private http: HttpClient,
  ) {}
  
  private log(message: string) {
    this.loggingService.add('App just used a HeaderButtonService to ' + message);
  }
  
  getButtons(): Observable<NavButton[]> {
    return this.http.get<NavButton[]>(this.buttonsURL).pipe(
      tap(heroes => this.log(`fetch the main header buttons`)),
      catchError(this.handleError('getButtons', []))
    );
  }
  
  private handleError<T> (action = 'action', result ?: T) {
    return (error: any): Observable<T> => {

      console.error(error); // log to console

      this.log(`${action} failed: ${error.message}`);

      // let app continue running
      return of(result as T);
    };
  }
  

}
