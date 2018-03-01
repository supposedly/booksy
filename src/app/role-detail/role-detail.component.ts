import { Component, OnInit, ViewChild, ChangeDetectorRef } from '@angular/core';
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
    private route: ActivatedRoute,
    private changeDetectorRef: ChangeDetectorRef,
    private roleService: RoleService,
  ) {}
  
  ngOnInit() {
    this.rID = this.route.snapshot.paramMap.get('rID');
    if (this.rID == 'new') {
      this.permArr = this.maxArr = this.lockArr = null;
    } else {
      this.getArrs();
    }
  }
  
  keys(obj) {
    if (obj) { return Object.keys(obj); }
  }
  
  checkView() {
    return this.rID == 'new' || +this.globals.perms.raw > +this.rawPermNum;
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
