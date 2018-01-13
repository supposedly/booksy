import { Component } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';

import { ReportsService } from '../reports.service';

import { Globals } from '../globals';

@Component({
  selector: 'app-reports',
  templateUrl: './reports.component.html',
  styleUrls: ['./reports.component.css']
})
export class ReportsComponent /* implements OnInit */ {
  sortBy: string = null;
  buttons: any[] = [
    {name: 'Checkouts', value: false},
    {name: 'Overdue items', value: false},
    {name: 'Fines', value: false},
    {name: 'Holds', value: false},
 // {name: 'Items', value: false}
  ]
  
  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private reportsService: ReportsService,
    private globals: Globals
  ) {}

  onSortChange(item, value) {
    if (item=='on') {this.sortBy = value;}
  }
  
  onTypeChange(idx, event) {
    for (let i in this.buttons) {
      {this.buttons[i].value = i==idx;}
    }
  }
  
  any(): boolean {
    // because I can't do this from HTML for some reason
    return this.buttons.some(n => n);
  }
  
  getReport() {
    let arr = [];
    for (let btn of this.buttons) {
      arr.push(btn.value?this.sortBy:false);
    }
    if (!arr.some(n => n) || !this.sortBy) { return; }
    this.reportsService.getReport(...arr)
      .subscribe(
        resp => {
          this.globals.reportData = resp;
          this.globals.reportDataSortedBy = this.sortBy;
          this.router.navigate(['./view'], {relativeTo: this.route});
        });
  }
}
