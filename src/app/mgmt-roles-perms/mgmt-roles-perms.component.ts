import { Component, OnInit } from '@angular/core';

import { RoleService } from '../role.service';

import { Role } from '../classes';

import { Globals } from '../globals';

@Component({
  selector: 'app-mgmt-roles-perms',
  templateUrl: './mgmt-roles-perms.component.html',
  styleUrls: ['./mgmt-roles-perms.component.css']
})
export class MgmtRolesPermsComponent implements OnInit {
  roles: any = null;
  msg: string;
  
  constructor(
    public globals: Globals,
    public roleService: RoleService
  ) {}

  ngOnInit() {
    this.roleService.getAll()
      .subscribe(
        res => this.roles = res.roles.sort((a, b) => a.name.localeCompare(b.name)), // sort received roles alphabetically by name
        err => this.msg = err.error?err.error:'Error.'
      );
  }
  
  deleteRole(rID, index) {
    this.roleService.delete(rID)
      .subscribe(resp => this.roles.splice(index, 1));
  }

}
