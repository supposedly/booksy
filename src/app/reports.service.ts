import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { catchError, map, tap } from 'rxjs/operators';
import { Observable } from 'rxjs/Observable';

import { Role, HttpOptions } from './classes';
const httpOptions = HttpOptions;

import { Globals } from './globals';

// Handles fetching of library-specific reports.
@Injectable()
export class ReportsService {
  reportsURL = 'api/location/reports';
  reportDateURL = 'api/location/reports/last';
  
  constructor(
    private globals: Globals,
    private http: HttpClient
  ) {}
  
  getReport(liveReports: boolean, chks= false, ovds= false, fins= false, hlds= false, itms= false) {
    /* 
     * Grab either a live report (if !!liveReports) or a cached one from the previous Sunday (if !liveReports).
     * 
     * chks: checkouts
     * ovds: overdues
     * fins: fines  (why didn't I spell this normally??)
     * hlds: holds
     * itms: items  (seriously?)
     *
     * Only one of the above values may be truthy at a time, indicating that it's what should be grabbed.
     */
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
    // Grabs the date of the last cached report (or, really, the date of the last Sunday -- bc that's when report-caching runs)
    return this.http.get<any>(this.reportDateURL);
  }
}
