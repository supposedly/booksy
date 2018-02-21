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
    
    // Y'all have no idea how much of a GOSH-darned pain in the freaking NECK this was
    // to make asynchronous
    // Previously I'd had it do everything synchronously, so it would shoot a request
    // to the server and then go on *without* waiting for its response.
    // This worked *almost* everywhere, because the first time the server responds
    // to that request it gets cached in Globals.isLoggedIn and then this method would
    // refer to the cache from then on -- BUT it would fail as soon as the user refreshed the page,
    // booting them to the login screen because the cache variable wouldn't have had time
    // to be initialized yet.
    // Enter asynchronicity. To say it in Arabic, '3allalle 2albe' -- it made me about
    // tear my hair out -- because it kept either throwing itself into an infinite loop
    // or complaining about the return type of one of the nested observables.
    //
    // The infinite loop problem turned out to be because, in ./rerouting/rerouting-component.ts,
    // I had set it to swallow all returned HTTP errors by redirecting to the application's
    // checkout screen (a protected page). This worked back when I wasn't waiting on the server's
    // response, but then when I made it do that it started constantly checking this authentication
    // guard, then failing with HTTP 400, then handle that by redirecting to /home for which it
    // needed to check this authentication guard, then see it fail, then ... ad nauseam.
    //
    // And then the unassignable-type errs I just 'solved' by throwing the observables in their own functions
    // (MemberAuthService.refresh() and .verify())
    // and setting those functions' return type to 'any'. I don't see too much harm in circumventing
    // typechecking if the typechecking is the only thing halting an otherwise-functional method!
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
