import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Location } from '@angular/common';

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
  roleName: string;
  msg: string = null;
  rID: string;
  
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
    /* unused */
    if (obj) { return Object.keys(obj); }
  }
  
  getArrs() {
    this.roleService.getArrs(this.rID)
      .subscribe(
        seqs => {
          this.permArr = seqs.perms;
          this.maxArr = seqs.maxes;
          this.lockArr = seqs.locks;
          this.roleName = seqs.name;
        }
      );
  }
  
  makeArrs() {
    this.permArr = {
      names: {
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
      this.roleService.create(this.roleName, this.permArr.names, this.maxArr.names, this.lockArr.names)
        .subscribe(resp => {this.rID = resp.rid; this.msg = "Successfully created."}, err => this.msg = err.error?err.error:"Not allowed!");
    } else {
      this.roleService.modify(this.rID, this.roleName, this.permArr.names, this.maxArr.names, this.lockArr.names)
        .subscribe(_ => this.msg = "Successfully edited.", err => this.msg = err.error?err.error:"Not allowed!");
    }
  }
}
