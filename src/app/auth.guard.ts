import { Injectable } from '@angular/core';
import { Router, CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { Observable } from 'rxjs/Observable';

import { MemberAuthService } from './member-auth.service';

@Injectable()
export class AuthGuard implements CanActivate {
  isLoggedIn: boolean = false;
  
  constructor(
    private router: Router,
    private memberAuthService: MemberAuthService
  ) {}
  
  canActivate(next: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<boolean> | Promise<boolean> | boolean {
    let href: string = next.url.toString();
    if (Object.keys(next.queryParams).indexOf('redirect') > -1 && !(next.queryParams['redirect'])) {
      this.router.navigateByUrl(next.url.toString());
      return true;
    } else if (
      next.queryParams['redirect']
      || href.startsWith('login')
      || href.startsWith('signup')
  ) {
      return true;
    } else if (this.memberAuthService.verify()) {
      return true;
    }
    this.router.navigate(['/login'], {queryParams: state.url==='/'?{}:{returnURL: state.url}})
    return false;
  }
}
