import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';

import { LocationService } from '../location.service';

import { Globals } from '../globals';

@Component({
  selector: 'app-mgmt-accounts',
  templateUrl: './mgmt-accounts.component.html',
  styleUrls: ['./mgmt-accounts.component.css']
})
export class MgmtAccountsComponent implements OnInit {
  cont = 0;
  roles: any[] = [];
  
  constructor(
    public globals: Globals,
    private router: Router,
    private route: ActivatedRoute,
    private locationService: LocationService
  ) {}

  ngOnInit() {
    this.getMembers();
  }
  
  getMembers() {
    this.roles.length = 0;
    this.locationService.getAllMembers(this.cont)
      .subscribe(resp => this.roles = resp.sort((a, b) => a.name.localeCompare(b.name)));
  }
  
}
