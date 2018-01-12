import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { Globals } from './globals';

@Injectable()
export class SetupService {
  private namesURL: string = 'stock/attrs/names';
  
  constructor(
    private globals: Globals,
    private http: HttpClient
  ) {}
  
  getNames() {
    this.http.get(this.namesURL)
      .subscribe(names => this.globals.attrs = names);
  }
}
