import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

import { RoleService } from '../role.service';
import { LocationService } from '../location.service';

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
  deleteDown = false;
  wait = setTimeout;
  
  constructor(
    public globals: Globals,
    public router: Router,
    public roleService: RoleService,
    private locationService: LocationService
  ) {}
  
  ngOnInit() {
    this.locationService.getAllRoles()
      .subscribe(
        res => this.roles = res.roles.sort((a, b) => a.name.localeCompare(b.name)), // sort received roles alphabetically by name
        err => this.msg = err.error ? err.error : 'Error.'
      );
  }
  
  deleteRole(rID, index) {
    this.roleService.delete(rID)
      .subscribe(_ => this.roles.splice(index, 1));
  }
  
  disableDeleteDown() {
    // Necessary (albeit roundabout?) because otherwise clicking the
    // delete button will also register a click on the role box below it
    // and send you to the page of a role that was just deleted.
    // Interestingly, this didn't start happening until the day before
    // my due date.
    setTimeout(() => this.deleteDown = false, .01);
  }

}
