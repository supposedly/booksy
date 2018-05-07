import { Injectable } from '@angular/core';
import { Router, CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';

import { Observable } from 'rxjs/Observable';
import 'rxjs/add/observable/of';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/switchMap';

import { MemberAuthService } from './member-auth.service';
import { Globals } from './globals';


@Injectable()
export class AuthGuard implements CanActivate {
  isLoggedIn = false;
  
  constructor(
    private router: Router,
    private globals: Globals,
    private memberAuthService: MemberAuthService,
  ) {}
  
  canActivate(next: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<boolean> | boolean {
    const href: string = next.url.toString();
    if (Object.keys(next.queryParams).indexOf('redirect') > -1 && !(next.queryParams['redirect'])) {
      // This means we have an empty redirect parameter, so we should strip it
      // out & instead authenticate on the new stripped URL.
      this.router.navigateByUrl(next.url.toString());
      return true;
    } else if (
      next.queryParams['redirect']  // We're currently redirecting to another page, so we should authenticate once we get there.
      || href.startsWith('login')   // The login page should be accessible to people not logged in.
      || href.startsWith('signup')  // Ditto ^
      || this.globals.isLoggedIn    // Logged-in members should be able to go wherever.
    ) { return true; }
    
    /* 
     * This thing was so so SO incredibly hard to make asynchronous...
     * 
     * Previously I'd had it do everything synchronously, so it would shoot a request
     * to the server and then continue in the application *without* waiting for its response.
     * This worked *almost* everywhere, because the first time the server responds
     * to that request it gets cached in Globals.isLoggedIn and then this method would
     * refer to the cache from then on -- BUT it would fail as soon as the user refreshed the page,
     * booting them to the login screen because the cache variable wouldn't have had time
     * to be initialized yet.
     * Enter asynchronicity. In brief, it made me want to tear my hair out early --
     * -- because it kept either throwing itself into an infinite loop of attempted login
     * or complaining about the return type of one of its nested observables.
     *
     * The infinite loop problem turned out to be because, in ./rerouting/rerouting-component.ts,
     * I had set it to swallow all returned HTTP errors by redirecting to the application's
     * checkout screen (a protected page). This worked back when I wasn't waiting on the server's
     * response, but then when I STARTED doing that it became so that it constantly checked this auth
     * guard, then failed with HTTP 400, then handled that by redirecting to /home for which it
     * needed to check this authentication guard, then failed ... ad nauseam.
     *
     * And then the unassignable-type errors I just 'solved' by throwing the observables in their own functions,
     * MemberAuthService.refresh() and MemberAuthService.verify(), then setting their return types to 'any'.
     * I don't see too much harm in circumventing static typechecking if the typechecking is the only thing stopping
     * an otherwise-fine method from working!
     * 
     * ...I also learned from this ordeal that 'asynchronous' is not pronounced 'ay-sync-RAWN-ous'.
     */
    
    // Verification is asynchronous, so we want this function to return an observable that completes at
    // its leisure rather than returning a straight true/false value. Hence we use Observable.map() & co,
    // rather than Observable.subscribe() like everywhere else where we need non-Observables returned.
    return this.memberAuthService.verify()
      .switchMap(
        // Observable.switchMap() automatically masks the switchMapped observable by the first 'nested' observable returned.
        // This means that, for instance, the below line `return Observable.of(true)` will change this function's return value
        // into literally Observable.of(true), rather than Observable(Observable.of(true)).  (The latter would be the case
        // if I'd done .map() rather than .switchMap(), though.)
        res => {
          if (res.valid) {
            // {..., 'valid': true, ...} is returned by sanic-jwt when the passed token is authenticable & valid.
            return this.memberAuthService.getInfo()
              // and this means we can just go ahead with signin & authentication.
              .map(infoRes => {
                this.memberAuthService.saveToGlobals(infoRes.me);
                this.globals.isLoggedIn = true;
                return Observable.of(true);
              });
          }
          // A response containing {..., 'valid': false, ...} means that the access token or refresh
          // token we passed is expired. We thus need to grab a new one, i.e. to 'refresh' the token.
          return this.memberAuthService.refresh()
            .map(
              refRes => {
                if (refRes.access_token || refRes.valid) {
                  // This means we've been given the OK to continue browsing with a new refresh token,
                  // and so we can go ahead with signin & authentication.
                  return this.memberAuthService.getInfo()
                    .map(infoRes => {
                      this.memberAuthService.saveToGlobals(infoRes.me);
                      this.globals.isLoggedIn = true;
                      return true;
                    });
                }
                // Otherwise, if either of refRes.access_token or refRes.valid is false/null, we assume we've
                // been kicked out and go back to the login screen.
                this.router.navigate(['/login'], {queryParams: state.url === '/' ? {} : {returnURL: state.url}});
                return false;
              }
            );
        }
      )
      .catch(
        err => {
          // sanic-JWT returns an HTTP 400 error if either the access/refresh token pased isn't acceptable or
          // the user's browser doesn't have an authentication cookie saved.
          // This isn't *actually* an error, though, so we can handle it by just redirecting to the login screen.
          this.router.navigate(['/login'], {queryParams: state.url === '/' ? {} : {returnURL: state.url}});
          return Observable.of(false);
        }
      );
  }
}
