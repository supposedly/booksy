import { Component, OnInit, ViewChild, ChangeDetectorRef } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Location } from '@angular/common';

import { PermsComponent } from '../attrs/perms.component';
import { LocksComponent } from '../attrs/locks.component';
import { LimitsComponent } from '../attrs/limits.component';

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
  
  // ViewChild allows us to look into what's being input in the Perms/Limits/Locks
  // components, and use those values in here.
  @ViewChild(PermsComponent) private perms: PermsComponent;
  @ViewChild(LimitsComponent) private limits: LimitsComponent;
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
    if (this.rID === 'new') {
      this.permArr = this.maxArr = this.lockArr = null;
    } else {
      this.getArrs();
    }
  }
  
  keys(obj) {
    if (obj) { return Object.keys(obj); }
  }
  
  checkView() {
    const gRaw = +this.globals.perms.raw;
    return this.rID === 'new' || gRaw >= 127 || gRaw > +this.rawPermNum;
  }
  
  getArrs() {
    this.roleService.getArrs(this.rID)
      .subscribe(
        seqs => {
          this.rawPermNum = seqs.perms_raw;
          this.permArr = seqs.perms;
          this.maxArr = seqs.limits;
          this.lockArr = seqs.locks;
          this.roleName = seqs.name;
        }
      );
  }
  
  submit() {
    const sMaxArr = {}, sLockArr = {}; // initialize this to properly copy attrs to it:
    for (const i of Object.keys(this.limits.arr.names)) {
      sMaxArr[i] = this.limits.overrideArr.names[i] ? this.limits.overrideArr.names[i] : this.limits.arr.names[i];
    }
    for (const i of Object.keys(this.locks.arr.names)) {
      sLockArr[i] = this.locks.overrideArr.names[i] ? this.locks.overrideArr.names[i] : this.locks.arr.names[i];
    }
    if (this.rID === 'new') {
      this.roleService.create(this.roleName, this.perms.arr.names, sMaxArr, sLockArr)
        .subscribe(resp => {
          this.rID = resp.rid; this.msg = 'Successfully created.';
        },
        err => this.msg = err.error ? err.error : 'Not allowed!'
      );
    } else {
      this.roleService.modify(this.rID, this.roleName, this.perms.arr.names, sMaxArr, sLockArr)
        .subscribe(_ => this.msg = 'Successfully edited.', err => this.msg = err.error ? err.error : 'Not allowed!');
    }
  }
}
