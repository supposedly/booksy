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
  @Input() editable: boolean = true; // whether to just show these values instead of making them editable
  @Input('auxiliary') forMain: boolean = true; // whether it is outside the main roles/perms detail screen
  
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
      holds: this.forMain?null:254 // no sense in overriding holds max because items can't place holds. 254 == don't override
    }
  }
  
  ngOnChanges() {
    this.arr = [];
    if (this.inputArr && !Array.isArray(this.inputArr)) { // it's initialized to [array(0)] but when it has data it'll be {object}
      for (let i in this.inputArr.names) { // could probably one-line this with a map or something
        if (this.inputArr.names[i] > 250) { // transfer overrides to the overrideArr
          this.overrideArr.names[i] = this.inputArr.names[i];
          this.inputArr.names[i] = 0; // and reset them in the inputArr so they show up disabled and 0
        }
      }
    }
    this.arr = this.inputArr?this.inputArr:this.defaultArr;
  }
  
  keys(obj) {
    // to make Object.keys usable by the template without it saying Object is undefined
    if (obj) { return Object.keys(obj); }
  }
  
}
