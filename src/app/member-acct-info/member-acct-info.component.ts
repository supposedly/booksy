import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Location } from '@angular/common';

import { LocationService } from '../location.service';
import { MemberService } from '../member.service';
import { RoleService } from '../role.service';

import { Globals } from '../globals';

@Component({
  selector: 'app-member-acct-info',
  templateUrl: './member-acct-info.component.html',
  styleUrls: ['./member-acct-info.component.css']
})
export class MemberAcctInfoComponent implements OnInit {
  msg: string;
  uID: string;
  member: any;
  roles: any[] = [];
  showMediaLink: boolean = false;
  
  constructor(
    public location: Location,
    public globals: Globals,
    private route: ActivatedRoute,
    private roleService: RoleService,
    private memberService: MemberService,
    private locationService: LocationService
  ) {}

  ngOnInit() {
    this.uID = this.route.snapshot.paramMap.get('uID');
    this.locationService.getFilteredRoles()
      .subscribe(res => this.roles = res.roles.sort((a, b) => a.name.localeCompare(b.name)));
    if (this.uID == 'new') {
      this.makeInfo();
    } else {
      this.getInfo();
    }
  }
  
  checkValid(): boolean {
    let m = this.member;
    // i do Not Understand why the below is necessary and chaining && doesn't work
    // (I guess this is prettier than &&-chaining though)
    return [m.username, m.name, m.rid, this.uID=='new'?m.password:true].every(n => n);
  }
  
  getInfo() {
    this.locationService.getMemberInfo(this.uID)
      .subscribe(
        resp => {
          this.showMediaLink = resp.member.user_id != this.globals.uID;
          this.member = resp.member;
        }
      );
  }
  
  makeInfo() { // mocks a member object to prepare creating a new one
    this.member = {
      perms: {
        raw: 0
      },
      user_id: null,
      username: null,
      name: null,
      rid: null,
      rolename: null,
      manages: false,
      recent: null,
      password: null,
    }
  }
  
  submit() {
    if (this.uID == 'new') {
      this.locationService.createMember(this.member)
        .subscribe(resp => this.location.back(), err => this.msg = err.error?err.error:'Error.');
    } else {
      this.memberService.edit(this.member)
        .subscribe(resp => this.msg = 'Successfully edited.', err => this.msg = err.error?err.error:'Error.');
    }
  }
  
  removeMember() {
    this.locationService.removeMember(this.member.user_id)
      .subscribe(resp => this.location.back(), err => this.msg = err.error?err.error:'Error.')
  }

}

