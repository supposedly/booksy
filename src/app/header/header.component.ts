import { Component, OnInit } from '@angular/core';

import { NavButton } from '../classes';
import { HeadButtonService } from '../head-button.service';
import { MemberAuthService } from '../member-auth.service';
import { Globals } from '../session-info-globals';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.css']
})
export class HeaderComponent implements OnInit {
  buttons: NavButton[];
  
  constructor(
    private headButtonService: HeadButtonService,
    private memberAuthService: MemberAuthService,
    private globals: Globals
  ) {}

  ngOnInit() {
    this.getButtons();
  }
  
  getButtons(): void {
    this.headButtonService.getButtons()
      .subscribe(buttons => this.buttons = buttons);
  }
  
}
