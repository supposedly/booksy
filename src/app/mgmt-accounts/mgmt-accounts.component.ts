import { Component, OnInit } from '@angular/core';

import { MemberService } from '../member.service';

import { Globals } from '../globals';

@Component({
  selector: 'app-mgmt-accounts',
  templateUrl: './mgmt-accounts.component.html',
  styleUrls: ['./mgmt-accounts.component.css']
})
export class MgmtAccountsComponent implements OnInit {
  cont: number = 0;
  roles: any[] = [];
  
  constructor(
    public globals: Globals,
    private memberService: MemberService
  ) {}

  ngOnInit() {
    this.getMembers();
  }
  
  getMembers() {
    this.roles.length = 0;
    this.memberService.getAll(this.cont)
      .subscribe(resp => this.roles = resp.sort((a, b) => a.name.localeCompare(b.name)));
  }

}
