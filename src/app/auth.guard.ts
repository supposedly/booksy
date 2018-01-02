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
  ) { }
  
  canActivate(next: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<boolean> | Promise<boolean> | boolean {
    if(this.memberAuthService.verify()) {
      return true;
    }
    this.router.navigate(['/login'], {queryParams: {returnURL: state.url}})
    return false;
  }
}
