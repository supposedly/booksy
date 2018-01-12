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
    this.getArrs();
  }
  
  keys(obj) {
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
  
  submit() {
    console.log(this.permArr); console.log(this.lockArr); console.log(this.maxArr);
    this.roleService.modify(this.rID, this.permArr.names, this.maxArr.names, this.lockArr.names)
      .subscribe(_ => this.msg = "Successfully edited.", err => err.error?err.error:"Not allowed!");
  }
}
