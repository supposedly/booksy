import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';

import { ReportsService } from '../reports.service';

import { Globals } from '../globals';

@Component({
  selector: 'app-reports',
  templateUrl: './reports.component.html',
  styleUrls: ['./reports.component.css']
})
export class ReportsComponent implements OnInit {
  reportLive = null;
  lastReportDate = null;
  sortBy: string = null;
  buttons: any[] = [
    {name: 'Checkouts', value: false},
    {name: 'Overdue items', value: false},
    {name: 'Fines', value: false},
    {name: 'Holds', value: false}
  ];
  
  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private reportsService: ReportsService,
    private globals: Globals
  ) {}

  ngOnInit() {
    this.reportsService.getLastReportDate()
      .subscribe(resp => this.lastReportDate = resp.date);
  }

  onSortChange(item, value) {
    if (item === 'on') {this.sortBy = value; }
  }
  
  onTypeChange(idx, event) {
    // Handle selection of report type
    idx = idx.toString();
    for (const i of Object.keys(this.buttons)) {
      {this.buttons[i].value = i === idx; }
    }
  }
  
  any(): boolean {
    // because I can't do this from HTML for some reason
    return this.buttons.some(n => n);
  }
  
  getReport() {
    const flags = [];
    // tell backend to sort these values & return
    for (const btn of this.buttons) {
      flags.push(btn.value ? this.sortBy : false);
    }
    // if no reports selected, return
    if (!flags.some(n => n) || !this.sortBy || this.reportLive === null) { return; }
    this.reportsService.getReport(this.reportLive, ...flags)
      .subscribe(
        resp => {
          this.globals.reportData = resp;
          this.globals.reportDataSortedBy = this.sortBy;
          this.router.navigate(['./view'], {relativeTo: this.route});
        });
  }
}
