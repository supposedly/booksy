import { Component, OnInit } from '@angular/core';
import { Location } from '@angular/common';

import { Globals } from '../globals';

@Component({
  selector: 'app-report-view',
  templateUrl: './report-view.component.html',
  styleUrls: ['./report-view.component.css']
})
export class ReportViewComponent implements OnInit {
  date;
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
    this.date = this.globals.reportDate;
    this.data = this.globals.reportData[this.key];
  }
  
  check(res) {
    // yikes. Just a bunch of edge cases
    return res.length && (res.length === 1 ? res[0][0] && !(res[0] in ['0', 'null']) : true);
  }
  
  printReport() {
    const contents = document.getElementById('printable-report').innerHTML;
    const popup = window.open('', '_blank', 'top=0,left=0,height=100%,width=auto');
    popup.document.open();
    popup.document.write(`
      <html>
        <head>
          <style>
            * {
              font-family: 'Source Sans Pro', sans-serif;
              color: #232323;
            }
            h1 {
              margin-bottom: 0;
            }
            h3 {
              margin-top: 0;
              font-weight: normal;
              padding-left: 1em;
            }
            li ul {
              list-style: disc;
            }
            li:empty {
              display: none;
            }
          </style>
        </head>
        <body onload="window.print(); window.close()">${contents}</body>
      </html>
    `);
    popup.document.close();
  }

}
