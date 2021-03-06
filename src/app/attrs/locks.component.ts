import { Component, OnChanges, Input } from '@angular/core';

import { Globals } from '../globals';

@Component({
  selector: 'app-locks',
  templateUrl: './locks.component.html',
  styles: ['.b { font-weight: 400; } h3 { display: inline-block; }']
})
export class LocksComponent implements OnChanges {
  arr: any = [];
  
  @Input('arr') inputArr: any; // the array to modify
  @Input() editable = false; // if user doesn't have permissions to modify the values, just show them
  @Input('auxiliary') forMain = true; // if this is outside the main roles/perms detail screen
  
  constructor(public globals: Globals) {}
  
  defaultArr = {
    names: {
      checkouts: 0,
      fines: 0
    }
  };
  
  overrideArr = {
    names: {
      checkouts: null,
      fines: null
    }
  };
  
  ngOnChanges() {
    this.arr = [];
    if (this.inputArr && !Array.isArray(this.inputArr)) { // it's initialized to [array(0)] but when it has data it'll be {object}
      for (const i in this.inputArr.names) { // could probably one-line this with a map or something
        if (this.inputArr.names[i] > 250) {
          this.overrideArr.names[i] = this.inputArr.names[i];
          this.inputArr.names[i] = 0;
        }
      }
    }
    this.arr = this.inputArr ? this.inputArr : this.defaultArr;
  }
  
  keys(obj) {
    // to make Object.keys usable by the template without it saying Object is undefined
    if (obj) { return Object.keys(obj); }
  }

}
