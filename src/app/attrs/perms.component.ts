import { Component, Input } from '@angular/core';

import { Globals } from '../globals';

@Component({
  selector: 'app-perms',
  templateUrl: './perms.component.html'
})
export class PermsComponent {
  @Input() arr: any;
  @Input('just-view') editable: boolean = true;
  
  constructor(public globals: Globals) {}
  
  keys(obj) {
    if (obj) { return Object.keys(obj); }
  }
}
