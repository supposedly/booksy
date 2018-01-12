import { Component, OnInit } from '@angular/core';

import { RoleService } from '../role.service';

import { Role } from '../classes';

@Component({
  selector: 'app-mgmt-roles-perms',
  templateUrl: './mgmt-roles-perms.component.html',
  styleUrls: ['./mgmt-roles-perms.component.css']
})
export class MgmtRolesPermsComponent implements OnInit {
  roles: any = null;
  
  constructor(private roleService: RoleService) {}

  ngOnInit() {
    this.roleService.getAll()
      .subscribe(res => this.roles = res.roles)
  }

}
