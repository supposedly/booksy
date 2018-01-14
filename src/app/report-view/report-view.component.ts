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

}
