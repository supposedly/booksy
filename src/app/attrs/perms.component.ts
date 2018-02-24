import { Component, OnInit, Input } from '@angular/core';

import { Globals } from '../globals';

@Component({
  selector: 'app-perms',
  templateUrl: './perms.component.html'
})
export class PermsComponent implements OnInit {
  arr: any = [];
  
  @Input('arr') inputArr: any;
  @Input('just-view') editable: boolean = true;
  
  defaultArr = {
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
  
  constructor(public globals: Globals) {}
  
  ngOnInit() {
    this.arr = this.inputArr?this.inputArr:this.defaultArr
  }
  
  keys(obj) {
    if (obj) { return Object.keys(obj); }
  }
}
