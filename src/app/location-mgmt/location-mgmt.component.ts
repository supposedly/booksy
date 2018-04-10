import { Component, OnInit } from '@angular/core';

import { MemberAuthService } from '../member-auth.service';
import { ButtonService } from '../button.service';

import { NavButton } from '../classes';
import { Globals } from '../globals';

@Component({
  selector: 'app-location-mgmt',
  template: `
    <div id="container">
      <div id="spacer"></div>
      <app-generic-header [buttons]="buttons"></app-generic-header> <!-- the management header -->
      <router-outlet></router-outlet>
    </div>
  `,
  styleUrls: ['./location-mgmt.component.css']
})
export class LocationMgmtComponent implements OnInit {
  buttons: NavButton[] = null;
  
  constructor(
    public globals: Globals,
    private buttonService: ButtonService,
    private memberAuthService: MemberAuthService
  ) {}
  
  ngOnInit() {
    this.getButtons(this.globals.uID);
  }
  
  getButtons(uID): void {
    if (!this.buttons) {
      this.buttonService.getMgmtHeaderButtons(uID)
        .subscribe(resp => this.buttons = resp.buttons);
    }
  }

}
