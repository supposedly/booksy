import { Injectable } from '@angular/core';

import { HttpClient } from '@angular/common/http';

import { Observable } from 'rxjs/Observable';
import { of } from 'rxjs/observable/of';

import { HttpOptions, NavButton, SideButton } from './classes';

const httpOptions = HttpOptions;

// The header, sidebar, and "management subheader" buttons
// are all dynamic, varying depending on whether & with what permissions the
// current member is logged in.
// This handles fetching of what's to be displayed in the headers/sidebar.
@Injectable()
export class ButtonService {
  private mainHeaderButtonURL = 'stock/buttons/main-header';
  private mgmtHeaderButtonsURL = 'stock/buttons/mgmt-header';
  private sideButtonURL = 'stock/buttons/home-sidebar';
  mgmtHeaderButtons: Observable<NavButton[]> = null;
  sideButtons: Observable<SideButton[]> = null;
  
  constructor(
    private http: HttpClient
  ) {}
  
  getMainHeaderButtons(): Observable<any> {
    // HOME | HELP | ABOUT, up top
    // (probably not changing but I didn't want to hardcode them)
    return this.http.get<any>(this.mainHeaderButtonURL);
  }
  
  getSidebarButtons(uID: string): Observable<any> {
    // Collapsible sidebar that appears on the left in the logged-in HOME tab.
    // If the user doesn't have the appropriate permissions, the green "Reports"
    // button & bottom two red buttons (manage media & manage location) will not
    // be given.
    if (!this.sideButtons) {
      this.sideButtons = this.http.get<any>(this.sideButtonURL, {params: {uid: uID}})
      .shareReplay();
    }
    return this.sideButtons;
  }
  
  getMgmtHeaderButtons(uID: string): Observable<any> {
    // Under "manage location", the leftmost header button (location info) will be hidden
    // if the user doesn't have the Manage Location permission. Likewise with 'manage accounts'
    // and 'manage roles'.
    if (!this.mgmtHeaderButtons) {
      this.mgmtHeaderButtons = this.http.get<any>(this.mgmtHeaderButtonsURL, {params: {uid: uID}})
        .shareReplay();
    }
    return this.mgmtHeaderButtons;
  }
}
