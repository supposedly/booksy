import { Component, OnInit } from '@angular/core';
import { Location } from '@angular/common';

import { Globals } from '../globals';

@Component({
  selector: 'app-report-view',
  templateUrl: './report-view.component.html',
  styleUrls: ['./report-view.component.css']
})
export class ReportViewComponent implements OnInit {
  data;
  key;
  
  constructor(
    public location: Location,
    private globals: Globals
  ) {}

  ngOnInit() {
    this.data = this.globals.reportData;
    this.key = Object.keys(this.data)[0]
    this.data = this.data[this.key]
  }

}
