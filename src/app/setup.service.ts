import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { catchError, map, tap } from 'rxjs/operators';
import { Observable } from 'rxjs/Observable';

import { Role, HttpOptions } from './classes';
const httpOptions = HttpOptions;

import { Globals } from './globals';

@Injectable()
export class SetupService {
  private attrsURL: string = 'api/attrs';
  private permCheckURL: string = 'api/member/check-perms';
  
  constructor(
    private globals: Globals,
    private http: HttpClient
  ) {}
  
  getAttrs(uID) {
    this.http.get<any>(this.attrsURL)
      .subscribe(resp => {
        this.globals.attrs = resp.names;
        this.globals.locMediaTypes = resp.types;
        this.globals.locGenres = resp.genres;
        this.globals.locColor = resp.locColor || 0xf7f7f7;
      });
  }
  
  getPerms(uID) {
    return this.http.get<any>(this.permCheckURL)
      .subscribe(resp => {
        this.globals.perms = resp.perms;
        this.globals.rawPermNum = resp.raw;
      });
  }
}
