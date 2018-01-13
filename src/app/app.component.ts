import { Component, OnInit } from '@angular/core';

import { MemberAuthService } from './member-auth.service';
import { SetupService } from './setup.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  title = 'app';

  constructor(
    private setupService: SetupService,
    private memberAuthService: MemberAuthService
  ) { }

  ngOnInit() {
    this.memberAuthService.verify();
  }

}
