import { Component, OnInit } from '@angular/core';

import { ButtonService } from '../button.service';
import { MemberAuthService } from '../member-auth.service';

import { NavButton } from '../classes';
import { Globals } from '../globals';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.css']
})
export class HeaderComponent implements OnInit {
  buttons: NavButton[];
  headerStyle: any;
  
  constructor(
    public globals: Globals,
    public memberAuthService: MemberAuthService,
    private buttonService: ButtonService
  ) {
    this.headerStyle = {
      '--main-color': globals.locColor,
      '--active-color': globals.locActiveColor,
      '--depressed-color': globals.locDepressedColor
    }; // attempting to get header color scheme working...
  }
  
  ngOnInit() {
    this.getButtons();
  }
  
  getButtons(): void {
    this.buttonService.getMainHeaderButtons()
      .subscribe(resp => this.buttons = resp.buttons);
  }

}
