import { Component, OnInit } from '@angular/core';
import { Location } from '@angular/common';

import { Globals } from '../globals';

@Component({
  selector: 'app-report-view',
  templateUrl: './report-view.component.html',
  styleUrls: ['./report-view.component.css']
})
export class ReportViewComponent implements OnInit {
  sort;
  data;
  key;
  
  constructor(
    public location: Location,
    private globals: Globals
  ) {}

  ngOnInit() {
    this.sort = this.globals.reportDataSortedBy;
    this.key = Object.keys(this.globals.reportData)[0];
    this.data = this.globals.reportData[this.key];
  }
  
  check(res) {
    // yikes. Just a bunch of edge cases
    return res.length && (res.length==1?res[0][0] && !(res[0] in ['0', 'null']):true);
  }

}
