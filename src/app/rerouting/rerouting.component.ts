import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';

import { MemberAuthService } from '../member-auth.service';

@Component({
  selector: 'app-rerouting',
  templateUrl: './rerouting.component.html',
  styleUrls: ['./rerouting.component.css']
})
export class ReroutingComponent implements OnInit {
  redirect: string = '/';
  
  constructor(
    private memberAuthService: MemberAuthService,
    private router: Router,
    private route: ActivatedRoute
  ) {
    this.router.errorHandler = (error: any) => {
        this.router.navigate(['home']); // or redirect to default route
    }
  }
  ngOnInit() {
    if (this.memberAuthService.verify()) {
      this.router.navigate(['home'])
    }
    this.redirect = this.route.snapshot.queryParams['redirect'] || '/';
    this.router.navigateByUrl(this.redirect, {});
  }

}
