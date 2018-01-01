import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

import { MemberAuthService } from '../member-auth.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {
  public errmsg: string = null;
  isLocationRegistered: boolean;
  uID: string;
  password: string;
  lID: string;
  loading: boolean;
  pw;
  uid;
  lid;
    
  constructor(
    private memberAuthService: MemberAuthService,
    private router: Router,
  ) {}
  
  ngOnInit() {
    this.loading = false;
    this.isLocationRegistered = this.memberAuthService.isRegistered;
  }
  
  send(): void {
    this.memberAuthService.logIn(this.uID, this.password, this.lID)  // memberAuthService will now send this info, along with the location ID fetched from /auth/me
      .subscribe(resp => {
          // login successful
          this.router.navigate(['/']);
      },
      err => {
          // login failed
          this.errmsg = 'Username or password is incorrect';
          this.loading = false;
      }
    );
  }
  
}
