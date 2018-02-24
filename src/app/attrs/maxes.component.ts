import { Component, OnChanges, Input } from '@angular/core';

import { Globals } from '../globals';

@Component({
  selector: 'app-maxes',
  templateUrl: './maxes.component.html'
})
export class MaxesComponent implements OnChanges {
  arr: any = [];
  
  @Input('arr') inputArr: any;
  @Input('just-view') editable: boolean = true;
  
  defaultArr = {
    names: {
      checkout_duration: 0,
      renewals: 0,
      holds: 0
    }
  }
  
  constructor(public globals: Globals) {}
  
  ngOnChanges() {
    this.arr = this.inputArr?this.inputArr:this.defaultArr;
  }
  
  keys(obj) {
    if (obj) { return Object.keys(obj); }
  }
}
