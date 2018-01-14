import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Location } from '@angular/common';

import { LocationService } from '../location.service';
import { RoleService } from '../role.service';

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
  
  constructor(
    public location: Location,
    private route: ActivatedRoute,
    private roleService: RoleService,
    private locationService: LocationService
  ) {}

  ngOnInit() {
    this.uID = this.route.snapshot.paramMap.get('uID');
    this.roleService.getAll()
      .subscribe(res => this.roles = res.roles.sort((a, b) => a.name.localeCompare(b.name)));
    if (this.uID == 'new') {
      this.makeInfo();
    } else {
      this.getInfo();
    }
  }
  
  getInfo() {
    this.locationService.getMemberInfo(this.uID)
      .subscribe(resp => this.member = resp.member);
  }
  
  makeInfo() {
    this.member = {
      uid: null,
      username: null,
      name: null,
      rid: null,
      rolename: null,
      manages: false,
      recent: null,
      password: null
    }
  }
  
  submit() {
    if (this.uID == 'new') {
      this.locationService.createMember(this.member)
        .subscribe(resp => {this.uID = resp.uid, this.member.uid = resp.uid, this.msg = 'Successfully created.'}, err => this.msg = err.error?err.error:'Error.');
    } else {
      this.locationService.editMember(this.member)
        .subscribe(resp => this.msg = 'Successfully edited.', err => this.msg = err.error?err.error:'Error.');
    }
  }

}

