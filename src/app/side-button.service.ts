import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { Observable } from 'rxjs/Observable';
import { of } from 'rxjs/observable/of';

import { SideButton } from './classes';

@Injectable()
export class SideButtonService {
  private buttonsURL: string = 'stock/buttons/home-sidebar';
  private rID: string;
  buttons: Observable<SideButton[]> = null;
  
  constructor(
    private http: HttpClient,
  ) {}
  
  getButtons(uID: string): Observable<SideButton[]> {
    // gets sidebar buttons
    // (passes user ID so buttons can be supplied according to user's permissions)
    if (!this.buttons) {
      this.buttons = this.http.get<SideButton[]>(this.buttonsURL, {params: {uid: uID}})
      .shareReplay();
    }
    return this.buttons;
  }  

}
