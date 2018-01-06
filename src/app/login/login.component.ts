import { Component, OnInit, NgZone } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';

import { MemberAuthService } from '../member-auth.service';
import { Globals } from '../session-info-globals';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {
  public errmsg: string = null;
  loading: boolean = false;
  returnURL: string;
  isLocationRegistered: boolean = false;
  uID: string;
  password: string;
  lID: string;
  pw;
  uid;
  lid;
  numRe = /^\d+$/
    
  constructor(
    private globals: Globals,
    private memberAuthService: MemberAuthService,
    private router: Router,
    private route: ActivatedRoute,
    private zone: NgZone
  ) {}
  
  ngOnInit() {
    this.isLocationRegistered = this.memberAuthService.isRegistered;
    this.returnURL = this.route.snapshot.queryParams['returnURL'] || '/home';
    if (this.memberAuthService.verify()) {
      this.zone.run(() => window.location.href = this.returnURL);
    }
  }
  
  send(): void {
    this.memberAuthService.logIn(this.uID, this.password, this.lID)  // memberAuthService will now send this info, along with the location ID fetched from /auth/me
      .subscribe(
        resp => {
            // login successful
            this.zone.run(() => window.location.href = this.returnURL);
            this.globals.isLoggedIn = true;
        },
        err => {
            // login failed
            this.errmsg = 'Incorrect username or password';
            this.loading = false;
            this.globals.isLoggedIn = false;
        }
    );
  }
  
}
