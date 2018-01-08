import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { catchError, map, tap } from 'rxjs/operators';
import { Observable } from 'rxjs/Observable';
import { of } from 'rxjs/observable/of';

import { LoggingService } from './logging.service';

import { SideButton, HttpOptions } from './classes';

const httpOptions = HttpOptions;

@Injectable()
export class SideButtonService {
  private buttonsURL: string = 'stock/buttons/home-sidebar';
  private rID: string;
  buttons: Observable<SideButton[]> = null;
  
  constructor(
    private loggingService: LoggingService,
    private http: HttpClient,
  ) {}
  
  getButtons(uID: string): Observable<SideButton[]> {
    if (!this.buttons) {
      this.buttons = this.http.get<SideButton[]>(this.buttonsURL, {params: {uid: uID}}).pipe(
        tap(heroes => this.log(`fetch the sidebar buttons from remote server`)),
        catchError(this.handleError('getting sidebar buttons', []))
      )
      .shareReplay();
    }
    return this.buttons;
  }
  
  private log(message: string, error?: boolean) {
    this.loggingService.add(error?'sideButtonService: ':'App just used a SideButtonService to ' + message);
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
