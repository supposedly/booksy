import { Component, OnInit } from '@angular/core';

import { MemberAuthService } from '../member-auth.service';

import { Globals } from '../globals';

@Component({
  selector: 'app-home-page',
  templateUrl: './home-page.component.html',
  styleUrls: ['./home-page.component.css']
})
export class HomePageComponent implements OnInit {
  constructor(
    public globals: Globals,
    private memberAuthService: MemberAuthService
  ) {}
  
  ngOnInit() {
    this.memberAuthService.storeMeInfo();
  }
}
