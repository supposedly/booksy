import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';

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
    private router: Router,
    private route: ActivatedRoute,
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
  
  viewMember(mID) {
    // because this just does not want to work as a regular routerLink
    this.router.navigate(['../members/' + mID.toString()], {relativeTo: this.route});
  }

}
