import { Component, OnInit } from '@angular/core';

import { MemberAuthService } from '../member-auth.service';

import { Globals } from '../globals';

@Component({
  selector: 'app-location-mgmt',
  templateUrl: './location-mgmt.component.html',
  styleUrls: ['./location-mgmt.component.css']
})
export class LocationMgmtComponent implements OnInit {
  constructor(
    public globals: Globals,
    private memberAuthService: MemberAuthService
  ) {}
  
  ngOnInit() {
    /* will have already happened in HomePageComponent */
    //this.memberAuthService.storeMeInfo();
  }
}
