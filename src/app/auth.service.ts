import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/http';

@Injectable()
export class AuthService {

  constructor(
    private http: HttpClient
  ) { }
  
  login(uid:string, password:string)

}
