import { Component, OnChanges, Input } from '@angular/core';

import { Globals } from '../globals';

@Component({
  selector: 'app-locks',
  templateUrl: './locks.component.html',
  styles: ['.b { font-weight: 400; } h3 { display: inline-block; }']
})
export class LocksComponent implements OnChanges {
  arr: any = [];
  
  @Input('arr') inputArr: any;
  @Input('just-view') editable: boolean = true;
  @Input('auxiliary') forMain: boolean = true;
  
  constructor(public globals: Globals) {}
  
  defaultArr = {
    names: {
      checkouts: 0,
      fines: 0
    }
  }
  
  overrideArr = {
    names: {
      checkouts: null,
      fines: null
    }
  }
  
  ngOnChanges() {
    if (!Array.isArray(this.inputArr)) { // it's initialized to [] but when it has data it'll be {}
      for (let i in this.inputArr.names) { // could probably one-line this with a map or something
        if (this.inputArr.names[i] > 250) {
          this.overrideArr.names[i] = this.inputArr.names[i];
          this.inputArr[i] = 0;
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
