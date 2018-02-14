import { Injectable } from '@angular/core';
import { Router, CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';

import { Observable } from 'rxjs/Observable';
import 'rxjs/Rx'; // eh

import { MemberAuthService } from './member-auth.service';
import { Globals } from './globals';

///
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { HttpOptions } from './classes';

const httpOptions = HttpOptions;
///

@Injectable()
export class AuthGuard implements CanActivate {
  isLoggedIn: boolean = false;
  
  constructor(
    private router: Router,
    private globals: Globals,
    private memberAuthService: MemberAuthService,
    private http: HttpClient
  ) {}
  
  canActivate(next: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<boolean> | boolean {
    let href: string = next.url.toString();
    if (Object.keys(next.queryParams).indexOf('redirect') > -1 && !(next.queryParams['redirect'])) {
      this.router.navigateByUrl(next.url.toString());
      return true;
    } else if (
      next.queryParams['redirect']
      || href.startsWith('login')
      || href.startsWith('signup')
      || this.globals.isLoggedIn
    ) { return true; }
    
    return this.memberAuthService.verify()
      .switchMap(
        res => {
          if (res.valid) {
            return this.memberAuthService.getInfo()
              .map(res => {
                this.memberAuthService.saveToGlobals(res.me);
                this.globals.isLoggedIn = true;
                return Observable.of(true);
              });
          } else {
            return this.memberAuthService.refresh()
              .map(
                res => {
                  if (res.access_token || res.valid) {
                    return this.memberAuthService.getInfo()
                      .map(res => {
                        this.memberAuthService.saveToGlobals(res.me);
                        this.globals.isLoggedIn = true;
                        return true;
                      });
                  }
                  this.router.navigate(['/login'], {queryParams: state.url==='/'?{}:{returnURL: state.url}})
                  return false;
                }
              ); // .catch not necessary, right?
          }
        }
      )
      .catch(
        err => {
          this.router.navigate(['/login'], {queryParams: state.url==='/'?{}:{returnURL: state.url}});
          return Observable.of(false);
        }
      );
  }
}
