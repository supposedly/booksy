import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

import { catchError, map, tap } from 'rxjs/operators';

@Injectable()
export class MemberAuthService {
  private authURL = '/auth';
  private verifyURL = '/auth/verify';
  private infoURL = '/auth/me';
  private refreshURL = '/auth/refresh';
  public token: string;
  
  constructor(
    private http: HttpClient
  ) {
    this.token
  }
  
  login(uid: string, password: string): boolean {
    return this.http.post<>
  }
  
  isLoggedIn() {
    this.http.post
  }
  
  isLibrary() {
    return this.http.get
  }
}
