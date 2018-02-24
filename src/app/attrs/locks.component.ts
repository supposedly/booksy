import { Component, OnInit, Input } from '@angular/core';

import { Globals } from '../globals';

@Component({
  selector: 'app-locks',
  templateUrl: './locks.component.html'
})
export class LocksComponent implements OnInit {
  arr: any = [];
  
  @Input('arr') inputArr: any;
  @Input('just-view') editable: boolean = true;
  
  defaultArr = {
    names: {
      checkouts: 0,
      fines: 0
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
