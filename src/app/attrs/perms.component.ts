import { Component, OnChanges, Input } from '@angular/core';

import { Globals } from '../globals';

@Component({
  selector: 'app-perms',
  templateUrl: './perms.component.html',
  styles: ['.b { font-weight: 400; } h3 { display: inline-block; }']
})
export class PermsComponent implements OnChanges {
  arr: any = [];
  override: boolean = false; // if in an auxiliary screen allow overriding of role-defined perms
  
  @Input('arr') inputArr: any;
  @Input() editable: boolean = false;
  @Input('auxiliary') forMain: boolean = true;
  
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
  
  ngOnChanges() {
    this.arr = this.inputArr?this.inputArr:this.defaultArr;
  }
  
  keys(obj) {
    // to make Object.keys usable by the template without it saying Object is undefined
    if (obj) { return Object.keys(obj); }
  }
  
}
