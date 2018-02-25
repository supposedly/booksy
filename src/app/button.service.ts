import { Injectable } from '@angular/core';

import { HttpClient } from '@angular/common/http';

import { Observable } from 'rxjs/Observable';
import { of } from 'rxjs/observable/of';

import { HttpOptions, NavButton, SideButton } from './classes';

const httpOptions = HttpOptions;

@Injectable()
export class ButtonService {
  private mainHeaderButtonURL = 'stock/buttons/main-header';
  private mgmtHeaderButtonsURL: string = 'stock/buttons/mgmt-header';
  private sideButtonURL: string = 'stock/buttons/home-sidebar';
  mgmtHeaderButtons: Observable<NavButton[]> = null;
  sideButtons: Observable<SideButton[]> = null;
  
  constructor(
    private http: HttpClient
  ) {}
  
  getMainHeaderButtons(): Observable<any> {
    return this.http.get<any>(this.mainHeaderButtonURL);
  }
  
  getSidebarButtons(uID: string): Observable<any> {
    if (!this.sideButtons) {
      this.sideButtons = this.http.get<any>(this.sideButtonURL, {params: {uid: uID}})
      .shareReplay();
    }
    return this.sideButtons;
  }
  
  getMgmtHeaderButtons(uID: string): Observable<any> {
    if (!this.mgmtHeaderButtons) {
      this.mgmtHeaderButtons = this.http.get<any>(this.mgmtHeaderButtonsURL, {params: {uid: uID}})
        .shareReplay();
    }
    return this.mgmtHeaderButtons;
  }
}
