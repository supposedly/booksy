import { Component, OnInit } from '@angular/core';

import { MemberService } from '../member.service';

@Component({
  selector: 'app-mgmt-accounts',
  templateUrl: './mgmt-accounts.component.html',
  styleUrls: ['./mgmt-accounts.component.css']
})
export class MgmtAccountsComponent implements OnInit {
  cont: number = 0;
  roles: any[] = [];
  
  constructor(private memberService: MemberService) { }

  ngOnInit() {
    this.getMembers();
  }
  
  getMembers() {
    this.roles.length = 0;
    this.memberService.getAll(this.cont)
      .subscribe(resp => this.roles = resp.sort((a, b) => a.role.localeCompare(b.role)));
  }

}
