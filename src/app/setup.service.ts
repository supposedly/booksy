import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { Globals } from './globals';

@Injectable()
export class SetupService {
  private locMediaURL: string = 'api/location/media'
  private namesURL: string = 'stock/attrs/names';
  private mTypeURL: string = this.locMediaURL + '/types';
  private genreURL: string = this.locMediaURL + '/genres';
  private permCheckURL: string = 'api/member/check-perms';
  
  constructor(
    private globals: Globals,
    private http: HttpClient
  ) {}
  
  getNames(uID) {
    this.http.get(this.namesURL, {params: {uid: uID}})
      .subscribe(names => this.globals.attrs = names);
  }
  
  getMediaTypes(uID) {
    return this.http.get(this.mTypeURL, {params: {uid: uID}})
      .subscribe(types => this.globals.locMediaTypes = types);
  }
  
  getGenres(uID) {
    return this.http.get(this.genreURL, {params: {uid: uID}})
      .subscribe(genres => this.globals.locGenres = genres);
  }
  
  getPerms(uID) {
    return this.http.get<any>(this.permCheckURL, {params: {uid: uID}})
      .subscribe(resp => this.globals.canEditMedia = resp.can_edit_media);
  }
}
