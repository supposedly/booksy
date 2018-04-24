import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { catchError, map, tap } from 'rxjs/operators';
import { Observable } from 'rxjs/Observable';

import { Role, HttpOptions } from './classes';
const httpOptions = HttpOptions;

import { Globals } from './globals';

@Injectable()
export class ReportsService {
  reportsURL = 'api/location/reports';
  reportDateURL = 'api/location/reports/last';
  
  constructor(
    private globals: Globals,
    private http: HttpClient
  ) {}
  
  getReport(liveReports: boolean, chks= false, ovds= false, fins= false, hlds= false, itms= false) {
    return this.http.put( // This is really just a GET request, but I need to be able to send it as json
      this.reportsURL, {
        live: liveReports,
        get: {
          checkouts: chks,
          overdues: ovds,
          fines: fins,
          holds: hlds,
          items: itms
        }});
  }
  
  getLastReportDate() {
    return this.http.get<any>(this.reportDateURL);
  }
}
