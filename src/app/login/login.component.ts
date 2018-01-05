import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';

import { MemberAuthService } from '../member-auth.service';
//import { HeaderComponent } from '../header/header.component';

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
    //private headerComponent: HeaderComponent,
    private memberAuthService: MemberAuthService,
    private router: Router,
    private route: ActivatedRoute
  ) {}
  
  ngOnInit() {
    this.isLocationRegistered = this.memberAuthService.isRegistered;
    this.returnURL = this.route.snapshot.queryParams['returnURL'] || '/home';
  }
  
  send(): void {
    this.memberAuthService.logIn(this.uID, this.password, this.lID)  // memberAuthService will now send this info, along with the location ID fetched from /auth/me
      .subscribe(
        resp => {
            // login successful
            this.router.navigateByUrl(this.returnURL);
            //this.headerComponent.loggedIn();
        },
        err => {
            // login failed
            this.errmsg = 'Incorrect username or password';
            this.loading = false;
            //this.headerComponent.loggedOut();
        }
    );
  }
  
}
