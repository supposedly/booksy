import { Component, OnInit, NgZone } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';

import { MemberAuthService } from '../member-auth.service';
import { Globals } from '../globals';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {
  public msg: string = null;
  public err = false;
  loading = false;
  returnURL: string;
  isLocationRegistered = false;
  uID: string;
  password: string;
  lID: string;
  pw;
  uid;
  lid;
  numRe = /^\d+$/;
  
  constructor(
    private globals: Globals,
    private memberAuthService: MemberAuthService,
    private router: Router,
    private route: ActivatedRoute,
    private zone: NgZone
  ) {
    memberAuthService.verify();
  }
  
  ngOnInit() {
    this.isLocationRegistered = this.memberAuthService.isRegistered;
    this.returnURL = this.route.snapshot.queryParams['returnURL'] || '/home';
    if (this.globals.isLoggedIn) {
      // this.zone.run(() => window.location.href = this.returnURL);
      // window.location.href = this.returnURL;
      this.router.navigateByUrl(this.returnURL);
    }
  }
  
  send(): void {
    // memberAuthService will now send this info, along with the location ID fetched from /auth/me
    this.memberAuthService.logIn(this.uID, this.password, this.lID)
      .subscribe(
        resp => {
          if (resp) {
            this.memberAuthService.getInfo()
              .subscribe(res => {
                this.memberAuthService.saveToGlobals(res.me);
                this.globals.isLoggedIn = true;
                this.err = false;
                this.msg = 'Thank you! You may now navigate to the HOME tab.'; // this should never be shown!
                this.router.navigateByUrl(this.returnURL);
              }
            );
          } else {
            this.globals.isLoggedIn = false;
            this.msg = 'Invalid login credentials';
          }
        },
        err => {
          // login failed
          this.err = true;
          this.msg = 'Invalid login credentials';
          this.loading = false;
          this.globals.isLoggedIn = false;
        }
    );
  }
  
}
