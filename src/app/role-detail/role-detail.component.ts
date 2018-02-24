import { Component, OnInit, ViewChild } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Location } from '@angular/common';

import { PermsComponent } from '../attrs/perms.component';
import { LocksComponent } from '../attrs/locks.component';
import { MaxesComponent } from '../attrs/maxes.component';

import { RoleService } from '../role.service';

import { Globals } from '../globals';

@Component({
  selector: 'app-role-detail',
  templateUrl: './role-detail.component.html',
  styleUrls: ['./role-detail.component.css']
})
export class RoleDetailComponent implements OnInit {
  permArr;
  maxArr;
  lockArr;
  rawPermNum;
  roleName: string;
  msg: string = null;
  rID: string;
  
  @ViewChild(PermsComponent) private perms: PermsComponent;
  @ViewChild(MaxesComponent) private maxes: MaxesComponent;
  @ViewChild(LocksComponent) private locks: LocksComponent;
  
  constructor(
    public globals: Globals,
    public location: Location,
    private roleService: RoleService,
    private route: ActivatedRoute,
  ) {}
  
  ngOnInit() {
    this.rID = this.route.snapshot.paramMap.get('rID');
    if (this.rID == 'new') {
      this.makeArrs();
    } else {
      this.getArrs();
    }
  }
  
  keys(obj) {
    if (obj) { return Object.keys(obj); }
  }
  
  checkView() {
    if (+this.globals.rawPermNum > +this.rawPermNum || this.rID == 'new') {
      return true;
    }
    return null;
  }
  
  getArrs() {
    this.roleService.getArrs(this.rID)
      .subscribe(
        seqs => {
          this.rawPermNum = seqs.perms_raw;
          this.permArr = seqs.perms;
          this.maxArr = seqs.maxes;
          this.lockArr = seqs.locks;
          this.roleName = seqs.name;
        }
      );
  }
  
  makeArrs() {
    this.permArr = {
      names: { // put every attr here and globals.perms.names[i] will take care of hiding appropriate ones
          manage_location: false,
          manage_accounts: false,
          manage_roles: false,
          create_admin_roles: false,
          manage_media: false,
          generate_reports: false,
          return_items: false
      }
    }
    this.maxArr = {
      names: {
        checkout_duration: 0,
        renewals: 0,
        holds: 0
      }
    }
    this.lockArr = {
      names: {
        checkouts: 0,
        fines: 0
      }
    }
    this.roleName = 'New role';
  }
  
  submit() {
    if (this.rID == 'new') {
      this.roleService.create(this.roleName, this.perms.arr.names, this.maxes.arr.names, this.locks.arr.names)
        .subscribe(resp => {this.rID = resp.rid; this.msg = "Successfully created."}, err => this.msg = err.error?err.error:"Not allowed!");
    } else {
      this.roleService.modify(this.rID, this.roleName, this.perms.arr.names, this.maxes.arr.names, this.locks.arr.names)
        .subscribe(_ => this.msg = "Successfully edited.", err => this.msg = err.error?err.error:"Not allowed!");
    }
  }
}
