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
  
  constructor(
    public globals: Globals,
    public memberAuthService: MemberAuthService,
    private buttonService: ButtonService
  ) {}

  ngOnInit() {
    this.getButtons();
  }
  
  getButtons(): void {
    this.buttonService.getMainHeaderButtons()
      .subscribe(resp => this.buttons = resp.buttons);
  }
  
}
