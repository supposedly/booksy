import { Component, OnChanges, Input } from '@angular/core';

import { Globals } from '../globals';

@Component({
  selector: 'app-maxes',
  templateUrl: './maxes.component.html',
  styles: ['.b { font-weight: 400; } h3 { display: inline-block; }']
})
export class MaxesComponent implements OnChanges {
  arr: any;
  
  @Input('arr') inputArr: any; // the array to modify
  @Input('just-view') editable: boolean = true; // if user doesn't have permissions to modify the values, just show them
  @Input('auxiliary') forMain: boolean = true; // if this is outside the main roles/perms detail screen
  
  constructor(public globals: Globals) {}
  
  defaultArr = {
    names: {
      checkout_duration: 0,
      renewals: 0,
      holds: 0
    }
  }
  
  overrideArr = {
    names: {
      checkout_duration: null,
      renewals: null,
      holds: null
    }
  }
  
  ngOnChanges() {
    this.arr = [];
    if (this.inputArr && !Array.isArray(this.inputArr)) { // it's initialized to [array(0)] but when it has data it'll be {object}
      for (let i in this.inputArr.names) { // could probably one-line this with a map or something
        if (this.inputArr.names[i] > 250) {
          this.overrideArr.names[i] = this.inputArr.names[i];
          this.inputArr.names[i] = 0;
        }
      }
    }
    console.log(this.inputArr, this.overrideArr, this.defaultArr);
    this.arr = this.inputArr?this.inputArr:this.defaultArr;
  }
  
  keys(obj) {
    // to make Object.keys usable by the template without it saying Object is undefined
    if (obj) { return Object.keys(obj); }
  }
  
}
